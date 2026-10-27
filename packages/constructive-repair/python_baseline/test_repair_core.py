"""Unit tests: exact algebra, contract checks, and regression negatives."""
import unittest
from fractions import Fraction
from repair_core import (Field, rank_of_columns, free_obstruction_basis,
                         feasibility_certificate, min_menu_repair, admissible_under_conservation,
                         solve_columns, rref, matrix_from_columns,
                         product, inverse, check_triangle_gluing)

class RepairTests(unittest.TestCase):
    def test_rational_rank(self):
        F=Field()
        self.assertEqual(rank_of_columns(3,[(1,0,0),(2,0,0),(0,1,0)],F),2)

    def test_prime_field_rank(self):
        F=Field(3)
        self.assertEqual(rank_of_columns(2,[(1,1),(2,2)],F),1)

    def test_reject_composite_field(self):
        for p in [0,1,4,9,15,21]:
            with self.subTest(p=p), self.assertRaises(ValueError):
                Field(p)

    def test_reject_float(self):
        with self.assertRaises(TypeError):
            Field().c(0.1)
        with self.assertRaises(TypeError):
            Field(5).c(0.1)

    def test_reject_nonunit_denominator(self):
        with self.assertRaises(ValueError):
            Field(5).c(Fraction(1,5))

    def test_fraction_matrix_exact(self):
        F=Field()
        v=solve_columns(2,[(2,0),(0,3)],(1,1),F)
        self.assertEqual(v,[Fraction(1,2),Fraction(1,3)])

    def test_inconsistent_matrix(self):
        self.assertIsNone(solve_columns(2,[(1,0)],(0,1),Field()))

    def test_empty_direction_zero_residual(self):
        out=feasibility_certificate(2,[],[(0,0)],[],Field())
        self.assertEqual(out['status'],'EXACT_REPAIR_CERTIFIED')
        self.assertEqual(out['witnesses'],[[]])

    def test_empty_direction_nonzero_residual(self):
        out=feasibility_certificate(2,[],[(1,0)],[],Field())
        self.assertEqual(out['status'],'NO_REPAIR_IN_SELECTED_CLASS')

    def test_zero_obstruction_requires_nothing(self):
        F=Field()
        D=[(1,0,0)]
        R=[(3,0,0),(0,0,0)]
        self.assertEqual(free_obstruction_basis(3,D,R,F),[])
        self.assertEqual(min_menu_repair(3,D,R,[(0,1,0)], [99],F)['indices'],[])

    def test_min_free_repair_two(self):
        F=Field()
        D=[(1,0,0)]
        R=[(0,1,0),(0,0,1),(0,3,4)]
        basis=free_obstruction_basis(3,D,R,F)
        self.assertEqual(basis,[0,1])
        self.assertEqual(feasibility_certificate(3,D,R,[R[j] for j in basis],F)['status'], 'EXACT_REPAIR_CERTIFIED')

    def test_constrained_two_more_than_free_one(self):
        F=Field()
        out=min_menu_repair(3,[(1,0,0)],[(0,1,0)],[(0,1,1),(0,0,1)],[1,1],F)
        self.assertEqual(out['indices'],[0,1])

    def test_weighted_objective(self):
        F=Field()
        D=[(1,0,0)];R=[(0,1,0)];C=[(0,1,1),(0,0,1),(0,1,0)]
        self.assertEqual(min_menu_repair(3,D,R,C,[1,1,9],F)['indices'],[0,1])
        self.assertEqual(min_menu_repair(3,D,R,C,[5,5,2],F)['indices'],[2])

    def test_constraint_enforced(self):
        F=Field()
        C=[(0,1),(1,0)]
        allowed=admissible_under_conservation(C,[(0,1)],F)
        self.assertEqual(allowed,[False,True])
        self.assertEqual(min_menu_repair(2,[(1,0)],[(0,1)],C,[1,1],F,allowed)['status'], 'NO_REPAIR_IN_ADMISSIBLE_MENU')

    def test_invalid_costs(self):
        with self.assertRaises(ValueError):
            min_menu_repair(1,[],[(1,)],[(1,)],[-1],Field())
        with self.assertRaises(ValueError):
            min_menu_repair(1,[],[(1,)],[(1,)],[],Field())

    def test_invalid_mask(self):
        with self.assertRaises(ValueError):
            min_menu_repair(1,[],[(1,)],[(1,)], [1],Field(),allowed=[])

    def test_invert_matrix_rational(self):
        F=Field()
        A=[[1,2],[3,5]]
        B=inverse(A,F)
        self.assertEqual(product(A,B,F),[[1,0],[0,1]])

    def test_invert_matrix_prime(self):
        F=Field(5)
        A=[[2,3],[1,2]]
        B=inverse(A,F)
        self.assertEqual(product(A,B,F),[[1,0],[0,1]])

    def test_singular_inverse_fails(self):
        self.assertIsNone(inverse([[1,2],[2,4]],Field()))

    def test_holonomy_chord(self):
        F=Field(5)
        A01=[[1,1],[0,1]]
        A12=[[2,0],[0,1]]
        A02=[[1,0],[1,1]]
        U0=[[1,1],[0,1]]
        U1=[[1,0],[1,1]]
        U2=[[2,1],[1,1]]
        B01=product(product(U1,A01,F),inverse(U0,F),F)
        B12=product(product(U2,A12,F),inverse(U1,F),F)
        B02=product(product(U2,A02,F),inverse(U0,F),F)
        self.assertEqual(check_triangle_gluing(A01,A12,A02,B01,B12,B02,U0,F)['status'],'GLUING_CERTIFIED')
        B02bad=[[(2*a)%5 for a in row] for row in B02]
        self.assertEqual(check_triangle_gluing(A01,A12,A02,B01,B12,B02bad,U0,F)['status'],'HOLONOMY_OBSTRUCTION')

if __name__=='__main__':
    unittest.main()
