Human-in-the-Loop Philosophy
============================

Agent 是全自动的。但某些操作不应该全自动——发送邮件、支付、
删除数据。Middleware 系统在工具执行前插入可编程的检查点。

Why middleware, not tool-side config
-------------------------------------

最初我们把审批配置放在 Tool 上（``requires_approval = True``）。
但这有两个问题：

1. Tool 不知道自己什么时候"危险"——发送邮件在一个场景下
   需要审批，在另一个场景下不需要。配置应该在 Agent 层，不在 Tool 层。
2. Tool 需要感知 Middleware 的存在——Tool 是独立组件，
   不应该耦合审批逻辑。

Middleware 解决了这两个问题：配置全部在 ``HumanInTheLoopMiddleware``
上，Agent 遍历 middleware 列表调用 ``before_tool`` 钩子。
Tool 完全不知道 middleware 的存在。

The middleware list
-------------------

Agent 接受 ``middleware=[...]`` 列表，按顺序执行：

.. code-block:: text

   _execute_tool(action):
     for each middleware in self.middleware:
       proceed, modified = mw.before_tool(tool_name, input)
       if not proceed: return "rejected"
       input = modified
     tool.run(input)

多个 middleware 可以堆叠——审计日志 + 人工审批 + 未来更多类型，
都在同一个列表里。
