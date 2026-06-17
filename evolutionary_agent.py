import os
import json
import importlib
from typing import List, Dict, Any

class SkillManager:
    """管理已经成功固化的 Skills（类似于蛋白质库）"""
    def __init__(self, skill_dir="./skills"):
        self.skill_dir = skill_dir
        os.makedirs(skill_dir, exist_ok=True)
        # 初始化创建 __init__.py 使其成为可导入的包
        with open(os.path.join(skill_dir, "__init__.py"), "a"): pass

    def register_skill(self, name: str, code: str, description: str):
        """将成功的流程固化为 Skill 写入文件"""
        file_path = os.path.join(self.skill_dir, f"{name}.py")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f'"""\nDescription: {description}\n"""\n\n')
            f.write(code)
        print(f"🧬 Skill 固化成功: {name}")

    def get_skills_manifest(self) -> List[Dict[str, str]]:
        """获取当前所有可用 Skill 的描述，供 Agent 规划时参考"""
        manifest = []
        for file in os.listdir(self.skill_dir):
            if file.endswith(".py") and not file.startswith("__"):
                name = file[:-3]
                # 简单读取描述
                with open(os.path.join(self.skill_dir, file), "r", encoding="utf-8") as f:
                    doc = f.read().split('"""')[1].strip() if '"""' in f.read() else "No description"
                manifest.append({"name": name, "description": doc})
        return manifest


class PiEvolutionAgent:
    """基于 pi-coding-agent 封装的自进化智能体"""
    def __init__(self, main_goal: str):
        self.main_goal = main_goal
        self.remaining_subgoals = [main_goal] # 初始时剩余目标为总目标
        self.skill_manager = SkillManager()
        self.loop_count = 0

    def call_pi_coding_agent(self, prompt: str) -> str:
        """
        模拟调用 @earendil-works/pi-coding-agent
        实际应用中，这里应替换为调用该 Agent 的 API 或命令行工具
        """
        # 这里的 prompt 会包含：当前可用的 skills、当前要解决的子目标、需要输出的测试用例
        print("🤖 pi-coding-agent 正在生成工作流程与代码...")
        
        # 伪代码：实际需调用 pi-coding-agent 生成 Python 代码
        # 生成的代码必须包含：1. 解决逻辑  2. 验证该逻辑的 assert 语句
        generated_code = """
def solve_partial_task():
    # 逻辑代码
    result = "partial_success"
    return result

# 自动化测试断言
assert solve_partial_task() == "partial_success"
"""
        return generated_code

    def execute_and_test(self, code: str) -> bool:
        """执行生成的流程，若断言通过则视为部分成功"""
        try:
            # 安全起见，实际应用建议在沙箱或子进程中运行
            local_vars = {}
            exec(code, globals(), local_vars)
            return True
        except Exception as e:
            print(f"❌ 流程运行或测试失败: {e}")
            return False

    def check_total_completion(self) -> bool:
        """检查总目标是否已达成"""
        # 实际应用中，可通过另一个 LLM 充当裁判，评估当前 Skill 库是否已覆盖总目标
        return len(self.remaining_subgoals) == 0

    def evolve_loop(self):
        """核心循环：规划 -> 尝试 -> 固化 -> 再规划"""
        while not self.check_total_completion() and self.loop_count < 10:
            self.loop_count += 1
            print(f"\n🔄 --- 开始第 {self.loop_count} 轮进化循环 ---")
            
            # 1. 收集当前的“基因库”（现有 Skills）
            available_skills = self.skill_manager.get_skills_manifest()
            
            # 2. 构造 Prompt，告诉 Agent 当前进度和剩余目标
            prompt = f"""
            总目标: {self.main_goal}
            当前已有的 Skill 库 (可在代码中 import skills.<name>): {json.dumps(available_skills)}
            当前需要解决的问题: {self.remaining_subgoals[0]}
            
            请利用现有 Skill（如有必要）构建一个新的分布式工作流程（Python 代码）。
            代码中必须包含至少一个显式的 assert 语句来验证本次局部目标是否达成。
            """
            
            # 3. 让 pi-coding-agent 编写工作流代码
            code_proposal = self.call_pi_coding_agent(prompt)
            
            # 4. 运行并测试该流程
            success = self.execute_and_test(code_proposal)
            
            if success:
                # 5. 成功：做成 Skill 固化下来
                skill_name = f"skill_step_{self.loop_count}"
                self.skill_manager.register_skill(
                    name=skill_name, 
                    code=code_proposal, 
                    description=f"解决了: {self.remaining_subgoals[0][:30]}..."
                )
                
                # 6. 更新目标状态（实际应用中需动态评估剩余什么任务）
                print(f"✅ 成功攻克阶段性目标！")
                # 假设任务被递进解决，这里移出已完成的，加入新的（此处仅作示意）
                self.remaining_subgoals.pop(0) 
                if self.loop_count == 3: # 模拟第3轮全部搞定
                    break
            else:
                # 7. 失败：什么都不做，下一轮重新针对该目标生成不同策略
                print(f"⚠️ 本轮尝试失败，不固化任何 Skill。准备重新规划。")

        print("\n🏁 进化结束。总目标达成或达到最大循环次数。")

# --- 运行示例 ---
if __name__ == "__main__":
    # 设定一个复杂目标
    target_problem = "抓取特定网页数据，清洗出价格字段，计算平均值，并生成可视化图表"
    
    agent = PiEvolutionAgent(main_goal=target_problem)
    agent.evolve_loop()

