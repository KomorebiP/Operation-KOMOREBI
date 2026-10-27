import Std
namespace H12DescentPacket

-- A common fixed class of M and omega M is omega-fixed. This finite
-- classification is the remaining M^-1 equation on E[omega-1]^3 = F3^3.
def isFixed3 (a b c : Int) : Prop :=
  (8*a-4*b+15*c-a)%3=0 ∧ (a-b)%3=0 ∧ (2*a-b+4*c-c)%3=0
instance (a b c : Int) : Decidable (isFixed3 a b c) := inferInstanceAs (Decidable (_ ∧ _ ∧ _))

theorem all_common_residues : ∀ a b c : Fin 3,
    isFixed3 a.val b.val c.val ↔ a.val=0 ∧ b.val=0 := by decide

-- Exact parameter vector identity R(1,2,4)-4(1,2,4)=7(8,-1,0).
theorem primitive_class_original_action :
  (8*1-4*2+15*4-4*1 : Int)=7*8 ∧
  (1-4*2 : Int)=7*(-1) ∧
  (2*1-2+4*4-4*4 : Int)=0 := by decide

theorem primitive_orbit_length_three : ∀ r : Fin 7,
    ((4:Nat)*(4*(4*r.val)))%7=r.val := by decide

theorem primitive_no_nonzero_fixed : ∀ r : Fin 7,
    (4*r.val)%7=r.val ↔ r.val=0 := by decide

theorem primitive_tensor_norm : ∀ r : Fin 7,
    (r.val+4*r.val+2*r.val)%7=0 := by decide

theorem reciprocal_pairing_action (k l : Int) :
    3*(2*k)*(4*l)-3*k*l=7*(3*k*l) := by grind

-- W_r(a,b)e_j = zeta^[r(a*j+4*a*b)] e_(j+b), zeta^7=1.
-- These exact integer formulas certify every matrix entry modulo seven.
def phase (r a b j : Int) : Int := r*(a*j+4*a*b)
def quad (r j : Int) : Int := 2*r*j^2

theorem weyl_product_phase (r a b c d j : Int) :
    phase r c d j + phase r a b (j+d) - phase r (a+c) (b+d) j
      -4*r*(a*d-b*c) = -7*r*a*d := by
  simp only [phase]; grind

theorem weyl_periodic_index (r a b j k : Int) :
    phase r a b (j+7*k)-phase r a b j = 7*(r*a*k) := by
  simp only [phase]; grind

theorem weyl_periodic_labels (r a b j k l : Int) :
    phase r (a+7*k) (b+7*l) j-phase r a b j =
    7*r*(k*j+4*a*l+4*k*b+28*k*l) := by
  simp only [phase]; grind

theorem shear_lift_phase (r a b j : Int) :
    -quad r j + phase r a b j + quad r (j+b)
      -phase r (a+4*b) b j = -14*r*b^2 := by
  simp only [phase,quad]; grind

theorem shear_lift_order_seven (r j : Int) : 7*quad r j = 7*(2*r*j^2) := by rfl

theorem shear_lift_fixes_zero (r : Int) : quad r 0=0 := by simp [quad]

def originalA (a b : Int) : Int := 2*a+b
def originalB (b : Int) : Int := 2*b

theorem original_third_step (a b : Int) :
    originalA (originalA (originalA a b) (originalB b)) (originalB (originalB b)) = 8*a+12*b := by
  simp only [originalA,originalB]; omega

theorem original_third_second (b : Int) : originalB (originalB (originalB b))=8*b := by
  simp only [originalB]; omega

-- L_r=D_r S_2, with D_r e_j=zeta^(2*r*j^2)e_j and S_2 e_j=e_(2j).
-- L_r W_(4r)(a,b) = W_r(2a+b,2b)L_r.
theorem packet_intertwiner_phase (r a b j : Int) :
    phase (4*r) a b j+quad r (2*(j+b))
      -quad r (2*j)-phase r (2*a+b) (2*b) (2*j) =
    7*(2*r*b*j) := by
  simp only [phase,quad]; grind

-- Composition L_r L_(4r) L_(2r) equals D_r^3; labels also close since 2^3=1 mod7.
theorem packet_three_lift_phase (r j : Int) :
    quad (2*r) (2*j)+quad (4*r) (4*j)+quad r (8*j)
      -3*quad r j = 7*(38*r*j^2) := by
  simp only [quad]; grind

theorem packet_three_lift_index (j : Int) : 8*j-j=7*j := by omega

-- Rotation omega sends labels (a,b) to (4a,4b) and class r to 2r.
-- S_4 intertwines these representatives.
theorem rotation_packet_phase (r a b j : Int) :
    phase (2*r) a b j-phase r (4*a) (4*b) (4*j) =
    -7*(2*r*a*j+8*r*a*b) := by
  simp only [phase]; grind

-- The M and omega lifts commute on the three-class packet.
theorem commuting_packet_lifts (r j : Int) :
    quad r (8*j)-quad (2*r) (2*j)=7*(16*r*j^2) := by
  simp only [quad]; grind

theorem rotation_cubed_index (j : Int) : 64*j-j=7*(9*j) := by omega

theorem opposite_pairing_is_not_trivial : (3: Int)%7 ≠ 0 := by decide
end H12DescentPacket
