from researchmind.cloud import CloudWorkspace
from researchmind.services.demo import load_demo, COLLECTION
from researchmind.services.science import Science

def test_demo_repeatable_and_isolated():
    a,b=CloudWorkspace(),CloudWorkspace()
    try:
        assert load_demo(a.library)==6
        assert load_demo(a.library)==0
        assert len(a.library.papers())==6
        assert len(b.library.papers())==0
        col=next(c for c in a.library.collections() if c.name==COLLECTION)
        assert len(a.library.members(col.id))==6
        for p in a.library.papers():
            assert p.abstract==""
            assert Science(a.sessions).sources(p.id)[0].provider=="Curated demo"
    finally:
        a.close()
        b.close()
