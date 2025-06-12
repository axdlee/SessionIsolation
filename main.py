from __future__ import annotations

from pkg.plugin.context import register, handler, BasePlugin, APIHost, EventContext
from pkg.plugin.events import PromptPreProcessing
from pkg.core import entities as core_entities

@register(name='SessionIsolation', description='群聊会话隔离插件', version='0.1.0', author='axdlee')
class SessionIsolation(BasePlugin):
    """群聊会话隔离插件，用于在群聊中为每个用户提供独立的会话上下文"""

    def __init__(self, host: APIHost):
        self.host = host
        super().__init__(host)
        self.host.ap.logger.info("[SessionIsolation] 插件已加载")

    async def initialize(self):
        """异步初始化"""
        pass

    @handler(PromptPreProcessing)
    async def on_prompt_preprocessing(self, ctx: EventContext):
        """处理群聊消息，根据之前的判断决定是否修改 launcher_id"""
        query = ctx.event.query

        # 只处理群聊消息
        if query.launcher_type != core_entities.LauncherTypes.GROUP:
            return
            
        # 构造新的 launcher_id，包含群组ID和发送者ID
        modified_launcher_id = f"{query.launcher_id}_{query.sender_id}"
        
        # 修改 query 的 launcher_id
        query.launcher_id = modified_launcher_id
        self.host.ap.logger.debug(f"[SessionIsolation] 修改 query 会话信息 - launcher_id: {modified_launcher_id}")
        
        # 修改 session 的 launcher_id
        query.session.launcher_id = modified_launcher_id
        self.host.ap.logger.debug(f"[SessionIsolation] 修改 session 会话信息 - launcher_id: {modified_launcher_id}")
        
        # 修改 variables 中的 session_id
        if query.variables:
            query.variables['session_id'] = f"{query.session.launcher_type.value}_{modified_launcher_id}"
            self.host.ap.logger.debug(f"[SessionIsolation] 修改 variables 会话信息 - session_id: {query.variables['session_id']}")

    def __del__(self):
        """析构函数"""
        self.host.ap.logger.info("[SessionIsolation] 插件已卸载")