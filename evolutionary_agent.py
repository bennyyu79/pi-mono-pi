import os
import json
import subprocess
import shutil
from typing import List, Dict

class SkillManager:
    """管理已经成功固化的 Skills（类似于生物体的蛋白质库）"""
    def __init__(self, skill_dir="./skills"):
        self.skill_dir = skill_dir
        os.makedirs(skill_dir, exist_ok=True)
        # 初始化创建 __init__.py 使其成为可导入的 Python 包
        with open(os.path.join(skill_dir, "__init__.py"), "a") as f:
            pass

    def register_skill(self, name: str, source_file_path: str):
        """将生成的成功脚本复制到 skill 库中"""
        target_path = os.path.join(self.skill_dir, f"{name}.py")
        shutil.copy(source_file_path, target_path)
        print(f"🧬 [DNA 表达] 成功固化新 Skill: {name}.py")

    def get_skills_context(self) -> str:
        """获取当前所有可用 Skill 的描述，作为 Prompt 注入"""
        skills = []
        for file in os.listdir(self.skill_dir):
            if file.endswith(".py") and not file.startswith("__"):
                skills.append(file)
        if not skills:
            return "当前没有任何可用 Skill。"
        return f"当前已成功固化的 Skill 列表（存放在 ./skills 目录下，你可以直接 import 它们）: {', '.join(skills)}"


class PiEvolvingSystem:
    """自进化智能体系统控制中心"""
    def __init__(self, total_goal: str):
        self.total_goal = total_goal
        self.skill_manager = SkillManager()
        self.current_workspace = "./agent_workspace"
        os.makedirs(self.current_workspace, exist_ok=True)
        self.loop_count = 0

    def call_real_pi_agent(self, prompt: str, step_name: str) -> str:
        """
        真正通过命令行调用 @earendil-works/pi-coding-agent
        """
        print(f"🤖 正在唤醒 pi-coding-agent 执行任务...")
        
        # 定义本次迭代生成的临时代码文件路径
        output_script = os.path.join(self.current_workspace, f"{step_name}.py")
        
        # 构造给 pi-coding-agent 的完整指令
        full_instruction = f"""
        你是一个专门编写 Python 脚本的编程智能体。
        
        【总体上下文与任务】
        {prompt}
        
        【强制输出要求】
        1. 请直接编写一个完整的 Python 脚本。
        2. 脚本中必须包含实现上述任务的代码逻辑。
        3. 脚本的底部必须包含自动化测试断言（Assert），用于自检本次任务是否完全成功。
        4. 请将最终的完整代码保存到文件：{output_script}
        """

        try:
            # 真正调用 pi-coding-agent 的 CLI 接口
            # 注意：请根据你安装的 npm 包的实际 CLI 命令调整 ["pi-agent", "run", ...]
            result = subprocess.run(
                ["pi", "code", "-p", full_instruction], 
                capture_output=True, 
                text=True, 
                check=True
            )
            print("🤖 pi-coding-agent 思考并生成完毕。")
            return output_script
        except subprocess.CalledProcessError as e:
            print(f"❌ 调用 pi-coding-agent 失败: {e.stderr}")
            return ""
        except FileNotFoundError:
            print("❌ 未在系统中找到 'pi-agent' 命令行工具，请确保已执行 npm install -g 安装。")
            return ""

    def verify_workflow(self, script_path: str) -> bool:
        """运行生成的 Python 脚本，通过断言(Assert)则代表成功"""
        if not script_path or not os.path.exists(script_path):
            return False
        
        print(f"🧪 正在运行断言测试: {script_path} ...")
        try:
            # 在独立子进程中运行脚本，防止崩溃影响主进程
            res = subprocess.run(["python", script_path], capture_output=True, text=True, timeout=30)
            if res.returncode == 0:
                print("✅ 测试通过！流程工作正常。")
                return True
            else:
                print(f"❌ 测试失败（断言未通过或运行时报错）:\n{res.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print("❌ 测试失败：代码运行超时。")
            return False

    def start_evolution(self):
        """核心进化循环：规划 -> 生产 -> 筛选 -> 固化"""
        # 实际应用中，可以通过一个轻量级大模型（如 GPT-4o-mini）来动态扣减目标
        # 这里用模拟的步骤目标来演示循环逻辑
        simulated_sub_goals = [
            "步骤1：编写代码请求 API 获取原始 JSON 数据，并将其保存到本地 raw.json",
            "步骤2：读取本地 raw.json，清洗掉空值，提取价格字段，计算出平均值",
            "步骤3：读取平均值数据，使用 matplotlib 绘制趋势图并保存为 chart.png"
        ]

        for current_task in simulated_sub_goals:
            self.loop_count += 1
            print(f"\n🔄 ======= 【第 {self.loop_count} 轮进化循环开始】 =======")
            
            # 1. 获取当前环境中所有已经进化出来的“蛋白质（Skills）”
            existing_skills = self.skill_manager.get_skills_context()
            
            # 2. 拼接当前轮次的 Prompt
            prompt_context = f"""
            最终总目标: {self.total_goal}
            
            当前可调用的基础设施（基因库）:
            {existing_skills}
            
            当前你需要解决的局部目标（剩下的问题）:
            {current_task}
            
            提示：如果之前的 Skill 对你有帮助，你可以在代码中 `from skills import skill_xxx` 来复用它。
            """
            
            # 3. 真正调用外部的 pi-coding-agent 生产代码
            step_name = f"skill_step_{self.loop_count}"
            generated_script = self.call_real_pi_agent(prompt_context, step_name)
            
            # 4. 环境选择压力测试（运行 Assert）
            is_success = self.verify_workflow(generated_script)
            
            if is_success:
                # 5. 成功：将其固化为 Skill 存入技能库
                self.skill_manager.register_skill(step_name, generated_script)
            else:
                # 6. 失败：什么都不做（丢弃该次生成的错误代码），下一轮针对该目标重新生成
                print(f"⚠️ 流程步骤运行失败。此代码被淘汰，不转为 Skill。系统将重试该目标。")
                # 在真实业务中，这里应该退回当前循环 index，让 Agent 换一种方案重新尝试该任务

        print("\n🏁 ======= 进化循环结束：所有目标已尝试攻克 =======\n")


# --- 运行入口 ---
if __name__ == "__main__":
    # 定义你想解决的复杂问题
    my_problem = "自动化获取电商数据、清洗并计算均值、最后生成可视化图表"
    
    # 实例化自进化系统
    evolving_agent = PiEvolvingSystem(total_goal=my_problem)
    
    # 启动系统
    evolving_agent.start_evolution()
