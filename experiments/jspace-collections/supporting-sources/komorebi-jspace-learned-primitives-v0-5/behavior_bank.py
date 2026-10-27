"""Editable memories with a measured behavior geometry. Author: Komorebi P."""
import copy,json
from pathlib import Path
import numpy as np
from editor import MemoryBank,point
from workspace import features
from geometry import BehaviorGeometry,measured_jacobian
from environment import observer

class BehaviorBank(MemoryBank):
    def __init__(self,model,geometry):
        super().__init__(model,geometry.transform)
        verified=getattr(geometry,"_verified_models",set())
        if self.model_hash not in verified:
            measured=measured_jacobian(observer(model),model.width)
            if measured.shape!=geometry.jacobian.shape or not np.allclose(measured,geometry.jacobian,rtol=1e-8,atol=1e-9):
                raise ValueError("Geometry/checkpoint mismatch.")
            geometry._verified_models=verified|{self.model_hash}
        self.geometry=geometry
        self.coordinate_info={"source":"valid output profiles and measured response Jacobian",
                              **geometry.diagnostics}

    def repair(self,name,tolerance=1e-7):
        """An explicit versioned operation; never changes the original evidence."""
        old=self.revision(name);h=self.geometry.repair(self.state(name))
        locks=old["locks"]
        worst=max([abs(self.row(s)@h-s["target"]) for s in locks.values()]+[0.])
        if worst>tolerance:
            return {"status":"conflict","reason":"Behavior repair conflicts with a retained requirement.",
                    "max_retained_error":float(worst)}
        previous=self.state(name)
        receipt={"status":"committed","workspace":name,
                 "primary_drift":float(np.max(abs(self.geometry.primary@(h-previous)))),
                 "unobserved_drift":float(np.max(abs(self.geometry.silent@(h-previous)))),
                 "behavior_residual_before":float(self.geometry.residual(previous)),
                 "behavior_residual_after":float(self.geometry.residual(h))}
        slot=self.slots[name];idx=len(slot["versions"]);receipt["revision"]=idx
        slot["versions"].append({"id":idx,"parent":old["id"],"state":h.tolist(),
                                "locks":copy.deepcopy(locks),"event":"value_preserving_behavior_repair",
                                "report":copy.deepcopy(receipt)})
        slot["current"]=idx
        return receipt

    def replay(self,name,o,passes=4,enforce_locks=True):
        if len(o["y"])!=1:raise ValueError("Replay one workspace at a time.")
        h=self.state(name)[None,:]
        phi=features(o["xy"]);locks=self.revision(name)["locks"]
        if locks and enforce_locks:
            rows=np.stack([self.row(s) for s in locks.values()])
            targets=np.array([s["target"] for s in locks.values()])
            pinv=np.linalg.pinv(rows@self.transform,rcond=1e-10)
        for cycle in range(passes):
            order=range(phi.shape[1]) if cycle%2==0 else range(phi.shape[1]-1,-1,-1)
            for t in order:
                h=self.model.step(h,phi[:,t],o["y"][:,t],o["channel"][:,t])
                h=self.geometry.repair(h)
                if locks and enforce_locks:
                    h[0]+=self.transform@(pinv@(targets-rows@h[0]))
        return h[0]

    def refine(self,name,o,passes=4,tolerance=1e-7):
        # Validate on a private bank, preserving the original on every rejection.
        trial=copy.deepcopy(self)
        try:
            result=MemoryBank.refine(trial,name,o,passes,tolerance)
        except ValueError as error:
            return {"status":"conflict","reason":str(error)}
        if result["status"]=="committed":
            result["behavior_residual"]=float(self.geometry.residual(trial.state(name)))
            self.slots=trial.slots
        return result

    def to_dict(self):
        obj=super().to_dict()
        obj["schema"]="komorebi_behavior_bank_v0.3"
        obj["behavior_geometry"]=self.geometry.to_dict()
        return obj

    @classmethod
    def load(cls,path,model):
        obj=json.loads(Path(path).read_text())
        if obj["schema"]!="komorebi_behavior_bank_v0.3":raise ValueError("Unknown bank schema.")
        b=cls(model,BehaviorGeometry.from_dict(obj["behavior_geometry"]))
        if b.model_hash!=obj["model_hash"]:raise ValueError("Bank/checkpoint mismatch.")
        saved_transform=np.asarray(obj["edit_coordinates"],float)
        if saved_transform.shape!=b.transform.shape or not np.allclose(saved_transform,b.transform,rtol=1e-10,atol=1e-12):
            raise ValueError("Saved edit coordinates disagree with behavior geometry.")
        # Preserve serialized coordinates exactly after validating their meaning.
        # Recomputing a pseudoinverse may change its final floating-point bits.
        b.transform=saved_transform
        b.slots=obj["slots"];b.coordinate_info=obj["coordinate_info"]
        for slot in b.slots.values():
            if not 0<=slot["current"]<len(slot["versions"]):raise ValueError("Invalid revision.")
            for i,v in enumerate(slot["versions"]):
                h=np.asarray(v["state"],float)
                if v["id"]!=i or h.shape!=(model.width,) or not np.all(np.isfinite(h)):raise ValueError("Invalid saved state.")
                if v["parent"] is not None and not 0<=v["parent"]<i:raise ValueError("Invalid parent.")
        return b
