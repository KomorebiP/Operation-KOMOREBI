"""Recover a realizable shared behavior space using measured responses.

Author: Komorebi P. Neural weights remain frozen. Valid output examples are
external supervision. This module contains no polynomial coefficients and no
sum/difference identities.
"""
import hashlib,json
import numpy as np

def array_hash(a):
    a=np.ascontiguousarray(a,dtype="<f8")
    return hashlib.sha256(a.tobytes()).hexdigest()

class GeometryError(ValueError):
    def __init__(self,status,diagnostics):
        self.status=status;self.diagnostics=diagnostics
        super().__init__(status)

def measured_jacobian(observe,width,epsilon=1e-4):
    probes=np.eye(width)*epsilon
    plus=np.asarray(observe(probes),float);minus=np.asarray(observe(-probes),float)
    if plus.shape!=minus.shape or plus.shape[0]!=width:
        raise ValueError("Observer returned invalid intervention responses.")
    return ((plus-minus)/(2*epsilon)).T

class BehaviorGeometry:
    def __init__(self,jacobian,basis,scales,anchors,diagnostics):
        self.jacobian=np.asarray(jacobian,float)
        self.basis=np.asarray(basis,float)
        self.scales=np.asarray(scales,float)
        self.anchors=np.asarray(anchors,int)
        self.diagnostics=dict(diagnostics)
        self.inverse=np.linalg.pinv(self.jacobian,rcond=1e-9)
        self.transform=(self.inverse@self.basis)*self.scales
        self.primary=self.jacobian[self.anchors]
        self.silent=np.eye(self.jacobian.shape[1])-self.inverse@self.jacobian
        anchor_map=self.primary@self.transform
        if len(self.anchors)!=self.transform.shape[1] or np.linalg.matrix_rank(anchor_map,tol=1e-9)!=len(self.anchors):
            raise GeometryError("primary_observations_do_not_identify_behavior",self.diagnostics)
        self.repair_matrix=self.transform@np.linalg.inv(anchor_map)@self.primary+self.silent

    @classmethod
    def recover(cls,observe,width,profiles,anchors,max_rank=8,rank_tolerance=1e-9,realization_tolerance=1e-7):
        targets=np.asarray(profiles,float)
        if targets.ndim!=2 or not np.all(np.isfinite(targets)):
            raise ValueError("Finite two-dimensional calibration profiles required.")
        _,s,vt=np.linalg.svd(targets,full_matrices=False)
        rank=int(np.sum(s>s[0]*rank_tolerance)) if len(s) and s[0]>0 else 0
        info={"profile_count":len(targets),"observables":targets.shape[1],
              "recovered_rank":rank,"maximum_rank":max_rank,"profile_sha256":array_hash(targets),
              "profile_singular_values":s.tolist(),"rank_tolerance":rank_tolerance,
              "realization_tolerance":realization_tolerance,"finite_difference_epsilon":1e-4,
              "coefficient_targets_used":False,"neural_weight_updates":False}
        if rank==0 or rank>max_rank:
            raise GeometryError("no_shared_space_within_budget",info)
        j=measured_jacobian(observe,width)
        if j.shape[0]!=targets.shape[1]:raise ValueError("Profiles and observer disagree.")
        basis=vt[:rank].T
        candidate=np.linalg.pinv(j,rcond=rank_tolerance)@basis
        residual=float(np.linalg.norm(j@candidate-basis)/np.linalg.norm(basis))
        info.update({"jacobian_rank":int(np.linalg.matrix_rank(j,tol=1e-9)),
                     "state_dimensions":width,"unobserved_dimensions":int(width-np.linalg.matrix_rank(j,tol=1e-9)),
                     "relative_realization_error":residual})
        if residual>realization_tolerance:
            raise GeometryError("behavior_outside_available_response_space",info)
        geometry=cls(j,basis,s[:rank]/np.sqrt(len(targets)),anchors,info)
        info.update({"repair_operator_norm":float(np.linalg.norm(geometry.repair_matrix,2)),
                     "repair_idempotence_error":float(np.linalg.norm(geometry.repair_matrix@geometry.repair_matrix-geometry.repair_matrix))})
        geometry.diagnostics=info
        return geometry

    def repair(self,states):
        """Preserve primary observations and all directions invisible to the panel."""
        return np.asarray(states)@self.repair_matrix.T

    def residual(self,states):
        output=np.asarray(states)@self.jacobian.T
        residual=output-output@self.basis@self.basis.T
        return np.max(np.abs(residual),axis=-1)

    def to_dict(self):
        return {"schema":"komorebi_behavior_geometry_v0.3","author":"Komorebi P.",
                "jacobian":self.jacobian.tolist(),"basis":self.basis.tolist(),
                "scales":self.scales.tolist(),"anchors":self.anchors.tolist(),
                "diagnostics":self.diagnostics}

    @classmethod
    def from_dict(cls,obj):
        if obj["schema"]!="komorebi_behavior_geometry_v0.3":raise ValueError("Unknown geometry.")
        return cls(obj["jacobian"],obj["basis"],obj["scales"],obj["anchors"],obj["diagnostics"])

def matched_feasible_edits(primary,reference_delta,rng,count=8):
    """Same primary response AND same Euclidean length, with random directions.

    These controls live in the full ambient space. They are not claimed to lie
    wholly outside the learned subspace. No test answers are read here.
    """
    c=np.asarray(primary,float);reference_delta=np.asarray(reference_delta,float)
    u,s,vt=np.linalg.svd(c,full_matrices=True)
    rank=int(np.sum(s>s[0]*1e-9))
    null=vt[rank:].T
    minimum=np.linalg.pinv(c,rcond=1e-9)@(c@reference_delta)
    remaining=float(reference_delta@reference_delta-minimum@minimum)
    if remaining < -1e-10:raise ValueError("Invalid norm matching.")
    radius=np.sqrt(max(0.,remaining))
    directions=rng.normal(size=(count,null.shape[1]))
    directions/=np.linalg.norm(directions,axis=1,keepdims=True)
    deltas=minimum[None,:]+radius*(directions@null.T)
    receipt={"primary_match_max":float(np.max(abs(deltas@c.T-reference_delta@c.T))),
             "norm_match_max":float(np.max(abs(np.linalg.norm(deltas,axis=1)-np.linalg.norm(reference_delta)))),
             "primary_null_dimensions":null.shape[1],"radius":float(radius)}
    return deltas,receipt
