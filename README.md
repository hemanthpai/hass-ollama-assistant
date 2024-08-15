[![GitHub Release](https://img.shields.io/github/release/hemanthpai/hass-ollama-assistant.svg?style=flat-square)](https://github.com/hemanthpai/hass-ollama-assistant/releases)
[![Downloads](https://img.shields.io/github/downloads/hemanthpai/hass-ollama-assistant/total?style=flat-square)](https://github.com/hemanthpai/hass-ollama-assistant/releases)
[![Build Status](https://img.shields.io/github/actions/workflow/status/hemanthpai/hass-ollama-assistant/validate.yml?style=flat-square)](https://github.com/hemanthpai/hass-ollama-assistant/actions/workflows/validate.yaml)
[![License](https://img.shields.io/github/license/hemanthpai/hass-ollama-assistant.svg?style=flat-square)](LICENSE)
[![hacs](https://img.shields.io/badge/HACS-default-orange.svg?style=flat-square)](https://hacs.xyz)

# THIS IS A WORK IN PROGRESS AND NOT READY FOR GENERAL USE. THIS NOTICE WILL BE REMOVED AND THE README UPDATED WHEN IT IS READY.

# Ollama Assistant

The Ollama Assistant integration adds an AI Assistant agent powered by [Ollama][ollama] in Home Assistant.

This assistant agent is able to control your house. The Ollama Assistant agent can be used in automations, but not as a [sentence trigger][sentence-trigger]. It can only query information that has been provided by Home Assistant. To be able to answer questions about your house, Home Assistant will need to provide Ollama with the details of your house, which include areas, devices and their states.

## Installation

To install the __Ollama Assistant__ integration to your Home Assistant instance, use this My button:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=ej52&repository=hass-ollama-conversation&category=integration)

#### Manual Insallation
If the above My button doesn’t work, you can also perform the following steps manually:

* Browse to your Home Assistant instance.
* Go to HACS > Integrations > Custom Repositories.
* Add custom repository.
  * Repository is `hemanthpai/hass-ollama-assistant`.
  * Category is `Integration`.
* Click ___Explore & Download Repositories___.
* From the list, select Ollama Assistant.
* In the bottom right corner, click the ___Download___ button.
* Follow the instructions on screen to complete the installation.

#### Note:
HACS does not "configure" the integration for you, You must add Ollama Assistant after installing via HACS.

* Browse to your Home Assistant instance.
* Go to Settings > Devices & Services.
* In the bottom right corner, select the ___Add Integration___ button.
* From the list, select Ollama Assistant.
* Follow the instructions on screen to complete the setup.

## Options
Options for Ollama Assistant can be set via the user interface, by taking the following steps:

* Browse to your Home Assistant instance.
* Go to Settings > Devices & Services.
* If multiple instances of Ollama Assistant are configured, choose the instance you want to configure.
* Select the integration, then select ___Configure___.

#### General Settings
Settings relating to the integration itself.

| Option                   | Description                                                                                                                                                                                                         |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| API Timeout              | The maximum amount of time to wait for a response from the API in seconds                                                                                                                                           |

#### System Prompt
The starting text for the AI language model to generate new text from. This text can include information about your Home Assistant instance, devices, and areas and is written using Home Assistant Templating.

#### Model Configuration
The language model and additional parameters to fine tune the responses.

| Option                   | Description                                                                                                                                                                                                         |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Model                    | The model used to generate response.                                                                                                                                                                                |
| Context Size             | Sets the size of the context window used to generate the next token.                                                                                                                                                |
| Maximum Tokens           | The maximum number of words or “tokens” that the AI model should generate in its completion of the prompt.                                                                                                          |
| Mirostat Mode            | Enable Mirostat sampling for controlling perplexity.                                                                                                                                                                |
| Mirostat ETA             | Influences how quickly the algorithm responds to feedback from the generated text. A lower learning rate will result in slower adjustments, while a higher learning rate will make the algorithm more responsive.   |
| Mirostat TAU             | Controls the balance between coherence and diversity of the output. A lower value will result in more focused and coherent text.                                                                                    |
| Temperature              | The temperature of the model. A higher value (e.g., 0.95) will lead to more unexpected results, while a lower value (e.g. 0.5) will be more deterministic results.                                                  |
| Repeat Penalty           | Sets how strongly to penalize repetitions. A higher value (e.g., 1.5) will penalize repetitions more strongly, while a lower value (e.g., 0.9) will be more lenient.                                                |
| Top K                    | Reduces the probability of generating nonsense. A higher value (e.g. 100) will give more diverse answers, while a lower value (e.g. 10) will be more conservative.                                                  |
| Top P                    | Works together with top-k. A higher value (e.g., 0.95) will lead to more diverse text, while a lower value (e.g., 0.5) will generate more focused and conservative text.                                            |


## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

### Discussions
Discussions for this integration over on [Home Assistant Community][discussions]

***

[ollama]: https://ollama.ai/
[ollama-github]: https://github.com/jmorganca/ollama
[sentence-trigger]: https://www.home-assistant.io/docs/automation/trigger/#sentence-trigger
[discussions]: https://community.home-assistant.io/t/custom-integration-ollama-conversation-local-ai-agent/636103
