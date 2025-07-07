from datetime import datetime
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage

from config import MAX_ROUNDS, model
from debate_state import DebateState
from debate_agents import create_agents
from react import react_reasoning


# ---------- 创建 Agents ----------
teacher, pros, cons = create_agents()

# ---------- 节点函数 ----------
def teacher_node(state: DebateState, phase: str) -> DebateState:
    """phase='opening' | 'debate' | 'closing'"""
    ctx = teacher._prompt(state["messages"])
    tip = {
        "opening": "请开场并邀请正方一辩。",
        "debate":  "请点评并继续。",
        "closing": "请总结辩论并宣布结束。"
    }[phase]
    content = model.invoke([HumanMessage(content=f"{ctx}\n\n{tip}")]).content
    msg = {"speaker": teacher.name, "content": content,
           "timestamp": datetime.now().isoformat()}

    new_state = {**state,
                 "messages": state["messages"] + [msg],
                 "current": ("teacher" if phase != "closing" else "teacher_close"),
                 "phase": ("debate" if phase == "opening" else phase),
                 "terminated": (phase == "closing")}
    return new_state


def pro_node(state: DebateState, idx: int) -> DebateState:
    agent = pros[idx]
    if idx == 0:  # Pro1 用 ReAct
        ctx = agent._prompt(state["messages"])
        content = react_reasoning(agent.name, ctx)
        msg = {"speaker": agent.name, "content": content,
               "timestamp": datetime.now().isoformat()}
        agent.memory.add(msg)
    else:
        msg = agent.reply(state["messages"])
    return {**state, "messages": state["messages"]+[msg],
            "current": f"pro{idx+1}"}


def con_node(state: DebateState, idx: int) -> DebateState:
    agent = cons[idx]
    if idx == 0:  # Con1 用 ReAct
        ctx = agent._prompt(state["messages"])
        content = react_reasoning(agent.name, ctx)
        msg = {"speaker": agent.name, "content": content,
               "timestamp": datetime.now().isoformat()}
        agent.memory.add(msg)
    else:
        msg = agent.reply(state["messages"])

    # 完成一整轮后 round+1
    new_round = state["round"] + (1 if idx == 2 else 0)
    return {**state, "messages": state["messages"]+[msg],
            "current": f"con{idx+1}", "round": new_round}


# ---------- 路由 ----------
def next_speaker(st: DebateState):
    if st["phase"] == "opening":
        return "pro1"          # 开场后轮到正方一辩

    if st["phase"] == "debate":
        order = ("teacher", "pro1", "con1", "pro2", "con2", "pro3", "con3")
        cur   = st["current"]
        nxt   = order[(order.index(cur) + 1) % len(order)]
        # 一轮结束 且 达到最大轮次 → 进入收尾
        if nxt == "teacher" and st["round"] >= MAX_ROUNDS:
            return "teacher_close"
        return nxt

    return END  # 其它情况收束


# ---------- 构建图 ----------
def build_graph():
    g = StateGraph(DebateState)

    # --- 各节点 ---
    g.add_node("teacher",        lambda s: teacher_node(s, "opening"))
    g.add_node("teacher_mid",    lambda s: teacher_node(s, "debate"))
    g.add_node("teacher_close",  lambda s: teacher_node(s, "closing"))

    g.add_node("pro1", lambda s: pro_node(s, 0))
    g.add_node("pro2", lambda s: pro_node(s, 1))
    g.add_node("pro3", lambda s: pro_node(s, 2))

    g.add_node("con1", lambda s: con_node(s, 0))
    g.add_node("con2", lambda s: con_node(s, 1))
    g.add_node("con3", lambda s: con_node(s, 2))

    # --- 条件边 ---
    g.add_conditional_edges("teacher",       next_speaker, {"pro1": "pro1"})
    g.add_conditional_edges("pro1",          next_speaker, {"con1": "con1"})
    g.add_conditional_edges("con1",          next_speaker, {"pro2": "pro2"})
    g.add_conditional_edges("pro2",          next_speaker, {"con2": "con2"})
    g.add_conditional_edges("con2",          next_speaker, {"pro3": "pro3"})
    g.add_conditional_edges("pro3",          next_speaker, {"con3": "con3"})
    g.add_conditional_edges("con3",          next_speaker,
        {"teacher": "teacher_mid", "teacher_close": "teacher_close"})
    g.add_conditional_edges("teacher_mid",   next_speaker, {"pro1": "pro1"})
    g.add_conditional_edges("teacher_close", lambda _: END, {END: END})

    g.set_entry_point("teacher")
    return g.compile()
