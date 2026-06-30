ModemTestPlatform/
├── configs/
├── data/
│   ├── caсhe/
│   ├── logs/
│   ├── reports/
│   └── workspace/
├── docs/
│   ├── 01_vision/
│   │   └── Vision.md
│   ├── 02_requirements/
│   │   └── Requirements Specification.md
│   ├── 03_glossary/
│   │   └── Glossary.md
│   ├── 04_domain/
│   │   └── Domain Model.md
│   ├── 05_architecture/
│   │   ├── Architecture Diagrams.md
│   │   └── Software_Architecture.md
│   ├── 06_engine/
│   │   ├── Events.md
│   │   ├── Execution Context.md
│   │   ├── Step.md
│   │   ├── Test Engine.md
│   │   ├── TestConfiguration.md
│   │   ├── TestPlan.md
│   │   └── TestRun.md
│   ├── 07_devices/
│   │   ├── Configuration.md
│   │   ├── Connection.md
│   │   ├── Device Adapter.md
│   │   ├── Device Manager.md
│   │   ├── Device.md
│   │   ├── Protocol.md
│   │   └── State Machine.md
│   ├── 08_measurements/
│   │   ├── Analysis.md
│   │   ├── Criterion.txt
│   │   ├── Measurement.md
│   │   ├── Metric.md
│   │   ├── Report.md
│   │   └── Verdict.md
│   ├── modem_answers/
│   │   ├── RX help.txt
│   │   ├── RX led.txt
│   │   ├── RX port connect message.txt
│   │   ├── RX print.txt
│   │   ├── RX reboot.txt
│   │   ├── RX stat.txt
│   │   ├── RX ttlstat.txt
│   │   ├── TX freq.txt
│   │   ├── TX help.txt
│   │   ├── TX led.txt
│   │   ├── TX port connect message.txt
│   │   ├── TX print.txt
│   │   ├── TX reboot.txt
│   │   └── TX stat.txt
│   ├── Modem Test Platform Documentation.md
│   ├── changelog.md
│   └── project_tree.md
├── scripts/
├── src/
│   ├── modem_test_platform/
│   │   ├── analysis/
│   │   │   ├── analyzer.py
│   │   │   ├── criterion.py
│   │   │   ├── metric.py
│   │   │   └── verdict.py
│   │   ├── api/
│   │   ├── cli/
│   │   │   ├── __init__.py
│   │   │   └── main.py
│   │   ├── core/
│   │   │   ├── constants.py
│   │   │   ├── events.py
│   │   │   ├── exceptions.py
│   │   │   ├── interfaces.py
│   │   │   └── state.py
│   │   ├── devices/
│   │   │   ├── adapters/
│   │   │   │   ├── base/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── adapter.py
│   │   │   │   ├── crossfire/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── crossfire_adapter.py
│   │   │   │   ├── flight_controller/
│   │   │   │   ├── jammer/
│   │   │   │   ├── mavlink/
│   │   │   │   └── __init__.py
│   │   │   ├── __init__.py
│   │   │   ├── configuration.py
│   │   │   ├── connection.py
│   │   │   ├── device.py
│   │   │   ├── manager.py
│   │   │   └── registry.py
│   │   ├── engine/
│   │   │   ├── __init__.py
│   │   │   ├── execution_context.py
│   │   │   ├── scheduler.py
│   │   │   ├── step.py
│   │   │   ├── test_engine.py
│   │   │   ├── test_plan.py
│   │   │   └── test_run.py
│   │   ├── measurements/
│   │   │   ├── collector.py
│   │   │   ├── measurement.py
│   │   │   └── storage.py
│   │   ├── protocols/
│   │   │   ├── base/
│   │   │   │   ├── __init__.py
│   │   │   │   └── protocol.py
│   │   │   ├── crossfire/
│   │   │   │   ├── models/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── link_state.py
│   │   │   │   ├── parsers/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── config_parser.py
│   │   │   │   │   ├── help_parser.py
│   │   │   │   │   ├── print_parser.py
│   │   │   │   │   ├── stat_parser.py
│   │   │   │   │   └── ttlstat_parser.py
│   │   │   │   ├── __init__.py
│   │   │   │   ├── commands.py
│   │   │   │   ├── config.py
│   │   │   │   ├── constants.py
│   │   │   │   ├── crossfire_protocol.py
│   │   │   │   └── parser.py
│   │   │   ├── mavlink/
│   │   │   ├── serial/
│   │   │   └── __init__.py
│   │   ├── reporting/
│   │   │   ├── generator.py
│   │   │   ├── html.py
│   │   │   ├── json.py
│   │   │   ├── pdf.py
│   │   │   └── report.py
│   │   ├── shared/
│   │   ├── storage/
│   │   │   ├── json/
│   │   │   ├── repositories/
│   │   │   ├── sqlite/
│   │   │   └── workspace.py
│   │   ├── transport/
│   │   │   ├── base/
│   │   │   ├── serial/
│   │   │   │   └── serial_transport.py
│   │   │   ├── __init__.py
│   │   │   ├── exceptions.py
│   │   │   ├── serial_port.py
│   │   │   ├── tcp.py
│   │   │   └── udp.py
│   │   ├── web/
│   │   └── __init__.py
│   └── tests/
│       └── protocols/
│           └── crossfire/
│               └── test_link_state_parser.py
├── tests/
├── ModemTestPlatform.zip
├── README.md
├── git.ignore
├── pyproject.toml
└── requirements.txt
