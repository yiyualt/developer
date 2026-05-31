Human-in-the-Loop Philosophy
============================

Agent 是全自动的——LLM 决定做什么，工具立刻执行。但某些操作
不应该全自动：发送邮件、支付、删除数据库。Human-in-the-Loop
在工具执行前插入人工审批节点。

Two halves of the contract
---------------------------

HITL 是 tool 和 agent 之间的双向约定：

.. code-block:: text

   Tool 侧:  requires_approval = True   → "我需要审批"
   Agent 侧: approver = ask_user       → "我有审批人"

   两者都设置时才生效。缺一不可：
   - tool 声明了但 agent 没 approver → 直接执行
   - agent 有 approver 但 tool 没声明 → 直接执行

Why built-in, not middleware?
------------------------------

第一个版本用了独立的 HumanInTheLoopMiddleware 包装类。
但它有三个问题：

1. 外部 monkey-patch Agent._execute_tool —— 脆弱
2. 和 Agent/ConversationalAgent 是两个类 —— 用户要学两个 API
3. 审批逻辑和 Agent 循环脱节 —— 审批失败后 Agent 不知道发生了什么

内置方案把 approver 作为 Agent 的一个可选参数。Agent 本身
负责审批流程——工具声明需求，Agent 执行检查。不需要额外的类。

Why not in callbacks?
----------------------

Callbacks 观察。HITL 控制。一个 callback 可以记录"工具被调用了"，
但不能说"别调这个工具"。HITL 需要控制权——拒绝或修改调用——这超出了
callback 的能力范围。
