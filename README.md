# FanScape (NeoForge 1.21.1)
Сборка: нужен JDK 21 и Gradle 8.x (или скопируйте gradlew/gradle/wrapper из официального NeoForge MDK).
  gradle build      -> build/libs/fanscape-1.0.0.jar
  gradle runClient  -> запуск для теста
В «Создать мир» -> Тип мира -> FanScape.
Настройка рельефа: src/main/resources/data/fanscape/worldgen/density_function/*.json и noise/*.json
(gen.py пересоздаёт все JSON и текстуры: python3 gen.py).

## GitHub Actions
Каждый push собирает jar (Actions -> Artifacts -> fanscape-jar). Workflow такой же, как в minetorio.
