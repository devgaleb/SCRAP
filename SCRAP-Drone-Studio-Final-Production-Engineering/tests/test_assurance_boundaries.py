import unittest
from server.verification import P,F,Trajectory,verify

class SafetyBoundaryTests(unittest.TestCase):
    def test_midsegment_collision_detected(self):
        t=Trajectory(frames=[F(at=0,positions=[P(x=-2,y=0,z=10),P(x=2,y=0,z=10)]),F(at=2,positions=[P(x=2,y=0,z=10),P(x=-2,y=0,z=10)])],min_separation=1,max_speed=5)
        r=verify(t)
        self.assertFalse(r['valid'])
        self.assertTrue(any(x['code']=='CONTINUOUS_SEPARATION' for x in r['issues']))
        self.assertFalse(r['certified'])
    def test_safe_separated_paths(self):
        t=Trajectory(frames=[F(at=0,positions=[P(x=0,y=0,z=10),P(x=0,y=20,z=10)]),F(at=5,positions=[P(x=5,y=0,z=10),P(x=5,y=20,z=10)])],min_separation=3,max_speed=3)
        r=verify(t)
        self.assertTrue(r['valid'])
        self.assertFalse(r['certified'])
    def test_bad_timing_rejected(self):
        t=Trajectory(frames=[F(at=1,positions=[P(x=0,y=0,z=10)]),F(at=1,positions=[P(x=1,y=0,z=10)])])
        self.assertFalse(verify(t)['valid'])
if __name__=='__main__':unittest.main()
