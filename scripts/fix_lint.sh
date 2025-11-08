#!/bin/bash
# Script to fix common linting issues

cd /home/user/ai-bot-misha

# Fix unused imports
sed -i 's/from app.bot.states.dialog import DialogStates, AIGenerationStates/from app.bot.states.dialog import AIGenerationStates/' app/bot/handlers/text_ai.py

# Fix scheduler.py imports
sed -i '/^from datetime import datetime$/d' app/core/scheduler.py
sed -i '/^from apscheduler.triggers.cron import CronTrigger$/d' app/core/scheduler.py
sed -i '/^from apscheduler.triggers.interval import IntervalTrigger$/d' app/core/scheduler.py

# Fix openai import
sed -i 's/import openai$//' app/services/ai/openai_service.py
sed -i 's/from typing import Optional, List, Dict$/from typing import Optional, List, Dict/' app/services/ai/openai_service.py

# Fix base.py
sed -i 's/from typing import Optional, Any$/from typing import Optional/' app/services/ai/base.py
sed -i 's/@dataclass$/\n@dataclass/' app/services/ai/base.py

# Fix comparison to True
sed -i 's/== True/.is_(True)/g' app/database/repositories/subscription.py

# Fix unused imports in various files
sed -i 's/from typing import Generic, TypeVar, Type, Optional, List, Any$/from typing import Generic, TypeVar, Type, Optional, List/' app/database/repositories/base.py
sed -i '/^from datetime import datetime$/d' app/services/subscription/subscription_service.py
sed -i '/^from datetime import datetime$/d' app/services/user/user_service.py
sed -i 's/from typing import TYPE_CHECKING, Optional$/from typing import TYPE_CHECKING/' app/database/models/referral.py
sed -i 's/, relationship$//' app/database/models/system.py

echo "✅ Fixed common linting issues"
