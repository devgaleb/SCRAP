from server.verification import Trajectory,verify

def test_crossing_detected_between_keyframes():
    t=Trajectory(frames=[{'at':0,'positions':[{'x':-5,'y':0,'z':10},{'x':5,'y':0,'z':10}]},{'at':10,'positions':[{'x':5,'y':0,'z':10},{'x':-5,'y':0,'z':10}]}],min_separation=2)
    result=verify(t)
    assert not result['valid']
    assert any(i['code']=='CONTINUOUS_SEPARATION' and i['time']==5 for i in result['issues'])

def test_parallel_safe():
    t=Trajectory(frames=[{'at':0,'positions':[{'x':0,'y':0,'z':10},{'x':0,'y':10,'z':10}]},{'at':10,'positions':[{'x':10,'y':0,'z':10},{'x':10,'y':10,'z':10}]}])
    assert verify(t)['valid']

def test_reject_bad_times():
    t=Trajectory(frames=[{'at':1,'positions':[{'x':0,'y':0,'z':10}]},{'at':1,'positions':[{'x':0,'y':0,'z':10}]}])
    assert not verify(t)['valid']
