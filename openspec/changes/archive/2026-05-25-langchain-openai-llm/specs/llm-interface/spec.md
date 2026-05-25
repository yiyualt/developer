## ADDED Requirements

### Requirement: LLM base class supports model configuration
LLM ABC SHALL accept optional common configuration parameters (`model_name`, `temperature`) that subclasses can use or override. These parameters SHALL be stored as instance attributes accessible to subclasses.

#### Scenario: Store model_name in base class
- **WHEN** an LLM subclass is instantiated with `model_name="gpt-4o-mini"`
- **THEN** `self.model_name` is available as `"gpt-4o-mini"` in the subclass