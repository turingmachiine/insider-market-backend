#!/bin/bash
# Скрипт для настройки PyCharm для проекта с src-структурой

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IDEA_DIR="$PROJECT_DIR/.idea"

echo "Настройка PyCharm для проекта..."

# Создаем директорию .idea если не существует
mkdir -p "$IDEA_DIR"

# Обновляем insider_market_backend.iml
cat > "$IDEA_DIR/insider_market_backend.iml" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<module type="PYTHON_MODULE" version="4">
  <component name="NewModuleRootManager">
    <content url="file://$MODULE_DIR$">
      <sourceFolder url="file://$MODULE_DIR$/src" isTestSource="false" />
      <sourceFolder url="file://$MODULE_DIR$/tests" isTestSource="true" />
      <excludeFolder url="file://$MODULE_DIR$/.venv" />
      <excludeFolder url="file://$MODULE_DIR$/.pytest_cache" />
      <excludeFolder url="file://$MODULE_DIR$/.mypy_cache" />
      <excludeFolder url="file://$MODULE_DIR$/logs" />
      <excludeFolder url="file://$MODULE_DIR$/data" />
    </content>
    <orderEntry type="jdk" jdkName="Python 3.12 (insider_market_backend)" jdkType="Python SDK" />
    <orderEntry type="sourceFolder" forTests="false" />
  </component>
  <component name="PyDocumentationSettings">
    <option name="format" value="PLAIN" />
    <option name="myDocStringFormat" value="Plain" />
  </component>
  <component name="TestRunnerService">
    <option name="PROJECT_TEST_RUNNER" value="py.test" />
  </component>
</module>
EOF

# Обновляем misc.xml
cat > "$IDEA_DIR/misc.xml" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="Black">
    <option name="sdkName" value="Python 3.12 (insider_market_backend)" />
  </component>
  <component name="MarkdownSettingsMigration">
    <option name="stateVersion" value="1" />
  </component>
  <component name="ProjectRootManager" version="2" project-jdk-name="Python 3.12 (insider_market_backend)" project-jdk-type="Python SDK">
    <output url="file://$PROJECT_DIR$/out" />
  </component>
  <component name="PyPACSettings">
    <option name="modified" value="True" />
  </component>
</project>
EOF

echo "✓ Настройки PyCharm обновлены"
echo ""
echo "Теперь выполните следующие действия в PyCharm:"
echo "1. File → Invalidate Caches... → Invalidate and Restart"
echo "2. После перезагрузки:"
echo "   - ПКМ на папку src → Mark Directory as → Sources Root"
echo "   - ПКМ на папку tests → Mark Directory as → Tests Root"
echo "3. Settings → Project → Project Structure:"
echo "   - Убедитесь, что src помечена как Sources"
echo "   - Убедитесь, что tests помечена как Tests"
echo "   - Если core, domain и т.д. помечены как Sources — уберите (выберите None)"
echo ""
echo "✓ Готово!"
