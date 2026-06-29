#!/usr/bin/env python3
"""Execute Merge - Automated merge execution with safety checks"""

import shutil
from pathlib import Path
from datetime import datetime

class MergeExecutor:
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.backup_dir = self.base_path / "backups" / datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def backup_files(self):
        """Create backup of original files"""
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        discussion_path = self.base_path.parent / "discussions" / "discussion_manager.py"
        orchestra_path = self.base_path / "ai_orchestra.py"
        
        if discussion_path.exists():
            shutil.copy2(discussion_path, self.backup_dir / "discussion_manager.py.bak")
            print(f"✅ Backed up discussion_manager.py")
        
        if orchestra_path.exists():
            shutil.copy2(orchestra_path, self.backup_dir / "ai_orchestra.py.bak")
            print(f"✅ Backed up ai_orchestra.py")
        
        return self.backup_dir
    
    def create_integrated_file(self):
        """Create integrated discussion manager with real AI"""
        
        # Read original discussion manager
        discussion_path = self.base_path.parent / "discussions" / "discussion_manager.py"
        with open(discussion_path, 'r') as f:
            discussion_content = f.read()
        
        # Create enhanced version with AI integration
        integrated_content = self._enhance_with_ai_integration(discussion_content)
        
        # Write to new file
        output_path = self.base_path / "integrated_discussion_manager.py"
        with open(output_path, 'w') as f:
            f.write(integrated_content)
        
        return output_path
    
    def _enhance_with_ai_integration(self, content: str) -> str:
        """Enhance discussion manager with AI orchestra integration"""
        
        # Add AI orchestra import
        ai_import = """
# AI Orchestra Integration
try:
    from ai_orchestra import AIOrchestra, AgentRole
    from smart_ai_router import SmartAIRouter
    AI_INTEGRATION_ENABLED = True
except ImportError:
    AI_INTEGRATION_ENABLED = False
"""
        
        # Insert after existing imports
        import_pos = content.find('TRACKING_ENABLED = False')
        if import_pos != -1:
            end_pos = content.find('\n', import_pos) + 1
            content = content[:end_pos] + ai_import + content[end_pos:]
        
        # Add AI integration to DiscussionManager class
        class_enhancement = """
    def __init__(self):
        self.threads_dir = Path(__file__).parent / "threads"
        self.threads_dir.mkdir(exist_ok=True)
        
        # Initialize tracking
        if TRACKING_ENABLED:
            self.session_tracker = SessionTracker()
            self.action_tracker = AIActionTracker()
        
        # Initialize AI integration
        if AI_INTEGRATION_ENABLED:
            self.ai_orchestra = AIOrchestra()
            self.ai_router = SmartAIRouter()
            print("🎭 AI Orchestra integration enabled")
        else:
            self.ai_orchestra = None
            self.ai_router = None
            print("⚠️  AI Orchestra not available - using mock responses")
    
    def _get_real_ai_response(self, participant: str, prompt: str, context: dict) -> str:
        \"\"\"Get real AI response using orchestra\"\"\"
        if not AI_INTEGRATION_ENABLED or not self.ai_orchestra:
            return self._get_mock_response(participant, prompt)
        
        try:
            # Map participant to agent role
            role_map = {
                "architect-ai": AgentRole.ARCHITECT,
                "security-ai": AgentRole.SECURITY,
                "performance-ai": AgentRole.PERFORMANCE,
                "cost-optimizer-ai": AgentRole.GENERAL,
                "devops-ai": AgentRole.GENERAL
            }
            
            role = role_map.get(participant, AgentRole.GENERAL)
            
            # Use smart router for cost optimization
            if self.ai_router:
                provider = self.ai_router.select_provider("moderate")
                print(f"🤖 Using {provider} for {participant}")
            
            # Get AI response via orchestra
            response = self.ai_orchestra.get_agent_response(role, prompt, context)
            
            # Track the action
            if TRACKING_ENABLED and self.action_tracker:
                self.action_tracker.track_action(
                    action_type="ai_discussion_response",
                    provider=provider if self.ai_router else "orchestra",
                    model=participant,
                    prompt_tokens=len(prompt.split()),
                    completion_tokens=len(response.split()),
                    cost=0.01,  # Estimated
                    latency=1.0,  # Estimated
                    success=True
                )
            
            return response
            
        except Exception as e:
            print(f"⚠️  AI response failed for {participant}: {e}")
            return self._get_mock_response(participant, prompt)
"""
        
        # Replace the __init__ method
        init_start = content.find('    def __init__(self):')
        if init_start != -1:
            # Find end of __init__ method
            init_end = content.find('\n    def ', init_start + 1)
            if init_end == -1:
                init_end = len(content)
            
            content = content[:init_start] + class_enhancement + content[init_end:]
        
        # Replace mock response calls with real AI calls
        content = content.replace(
            'response = self._get_mock_response(participant, prompt)',
            'response = self._get_real_ai_response(participant, prompt, discussion.context)'
        )
        
        return content

def main():
    import sys
    
    executor = MergeExecutor()
    
    print("🔄 Starting merge execution...")
    
    # Step 1: Backup
    backup_dir = executor.backup_files()
    print(f"📁 Backups created in: {backup_dir}")
    
    # Step 2: Create integrated file
    try:
        output_file = executor.create_integrated_file()
        print(f"✅ Created integrated file: {output_file}")
        
        print(f"\n🎯 Next steps:")
        print(f"1. Review: {output_file}")
        print(f"2. Test: python3 {output_file.name} create 'Test AI Integration' 'architect-ai,security-ai'")
        print(f"3. If successful, replace original discussion_manager.py")
        print(f"4. Restore from backup if needed: {backup_dir}")
        
    except Exception as e:
        print(f"❌ Merge failed: {e}")
        print(f"Original files preserved in: {backup_dir}")
        sys.exit(1)

if __name__ == "__main__":
    main()
