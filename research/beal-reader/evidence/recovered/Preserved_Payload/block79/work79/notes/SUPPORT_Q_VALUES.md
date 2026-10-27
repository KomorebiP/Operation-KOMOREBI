# B79.2. The actual upper values at beta support are forced after p is fixed

Let T,F be the compatible pro-seven tame generator and arithmetic Frobenius at
an actual depth-one beta-supporting place. Put c=beta(T)!=0, b=beta(F),
h=(Q-1)/7 mod7. The retained alpha is identically zero locally, so p and q are
ordinary local homomorphisms at this residual precision.

Block78 gives

    M=c[[theta,-theta^2],[1,-theta]],
    A=[[theta*b,theta*h-theta^2*b],[b,h-theta*b]],
    rho(T)=I+7M, rho(F)=I+7A mod49.

Write B0(F)=b0(F)/7 mod7. This is defined because alpha(F)=0. Reference inertia
is zero, and its Frobenius first digit is [[h,B0(F)],[0,0]]. Therefore

    p(T)=theta*c,  p(F)=theta*b-h,
    q(T)=-theta^2*c,
    q(F)+B0(F)=theta*h-theta^2*b=-theta*p(F).

Eliminating theta proves

    c p(F)-b p(T)=-h c,
    c q(T)=-p(T)^2,
    c (q(F)+B0(F))=-p(T)p(F).                         (4)

These are equations in ONE common global frame with ONE reference. In particular
B0(F) is not set to zero by a new local choice. Changing F to T^mF transforms the
values compatibly, and all three equations remain valid.

Conversely these equations reconstruct the displayed first-order toric packet.
That converse is about the packet, not an actual global curve or every further
integral lift.

For two full first-order deformations with the SAME p and beta and reference,
the upper difference xi is a k(chi) cocycle. Equations (4) give xi(T)=xi(F)=0 at
every beta-supporting place. Since the local coefficient action is trivial,
this means full local class-zero, not only unramifiedness. Thus

    xi|G_v=0 for all v in Ram(beta).                  (5)

Unrestricted H1 interpolation may enforce (5) at those finitely many places,
but is not thereby constrained at all additional bad divisors. Do not confuse
the finite homogeneous q-condition with a proof that all corrections are global
Frey deformations.
