from datetime import datetime
from debate_state import DebateState
from state_graph import build_graph
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

def main():
    print("\n" + "="*52)
    print("多智能体辩论系统  |  主题：AI对教育的应用的好坏")
    print("="*52)

    graph = build_graph()

    init: DebateState = dict(
        messages=[{"speaker": "System",
                   "content": "欢迎来到辩论！",
                   "timestamp": datetime.now().isoformat()}],
        current="teacher",
        phase="opening",
        round=0,
        terminated=False
    )

    for step in graph.stream(init):
        if isinstance(step, dict):
            # step 形如 {"node_name": state}
            state = list(step.values())[0]
            msg   = state["messages"][-1]
            print(f"\n{msg['speaker']}:\n{msg['content']}\n" + "-"*78)
            if state.get("terminated"):
                print("辩论完美结束")
                break

if __name__ == "__main__":
    main()
