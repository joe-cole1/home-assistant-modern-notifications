# Modern Multi-Device Notifications

A reusable Home Assistant 2026.7+ script blueprint for rich notifications to
multiple Home Assistant Companion devices.

It supports:

- multiple Companion recipients without requiring a notification group;
- common Android and iOS delivery options;
- image, video, audio, and camera-stream attachments;
- up to three event, text-reply, or link actions;
- first-response-wins behavior with collision-safe action identifiers;
- response timeouts and automatic clearing on every recipient;
- stable tags for replacement, updates, and explicit clearing;
- structured responses returned to the calling automation; and
- an advanced payload object for progress, chronometers, live updates, maps,
  TTS, wearable options, and future Companion features.

The blueprint deliberately focuses on notifications. Companion notification
commands that control the phone itself (Bluetooth, DND, flashlight, kiosk,
sensor refresh, and similar commands) are outside its typed API.

## Requirements

- Home Assistant 2026.7.0 or newer.
- Official Home Assistant Companion App recipients with notifications enabled.
- A unique Companion **Device ID** for every recipient. This is the device name
  under Companion App > your server, not merely the device-registry display
  name.

## Install

Import this URL from **Settings > Automations & scenes > Blueprints**:

```text
https://github.com/joe-cole1/home-assistant-modern-notifications/blob/main/notifications.yaml
```

Create a script from the imported blueprint and select its default Companion
`notify` entities. The examples below assume the resulting script entity is
`script.modern_multi_device_notifications`.

## Basic notification

```yaml
- action: script.modern_multi_device_notifications
  data:
    title: Laundry
    message: The washer has finished.
```

Calls without event or reply buttons return immediately with `status: sent`.

## Actionable notification

Call the script directly—not through `script.turn_on`—when the caller needs to
wait for and capture a response.

```yaml
- action: script.modern_multi_device_notifications
  data:
    title: Garage door
    message: The garage door is still open. Close it?
    action_1_title: Close
    action_1_key: close
    action_2_title: Leave open
    action_2_key: ignore
    response_timeout:
      minutes: 10
  response_variable: notification_result

- choose:
    - conditions: "{{ notification_result.status == 'action' and
      notification_result.action_key == 'close' }}"
      sequence:
        - action: cover.close_cover
          target:
            entity_id: cover.garage_door
```

The first event or text reply from any recipient wins. The script ignores
notification-cleared/swipe events and waits for a real response or the timeout.

## Text reply

```yaml
- action: script.modern_multi_device_notifications
  data:
    title: Set thermostat
    message: What temperature should I use?
    action_1_title: Reply
    action_1_key: temperature
    action_1_type: reply
    action_1_options:
      textInputButtonTitle: Set
      textInputPlaceholder: "68"
  response_variable: notification_result
```

The reply is returned as `notification_result.reply_text`.

## Replace and clear

Sending another notification with the same tag replaces the previous one:

```yaml
- action: script.modern_multi_device_notifications
  data:
    title: Backup progress
    message: 50% complete
    tag: backup-progress
    extra_data:
      progress: 50
      progress_max: 100
```

Clear it later from all selected recipients:

```yaml
- action: script.modern_multi_device_notifications
  data:
    operation: clear
    tag: backup-progress
```

## Advanced data

`extra_data` is merged recursively into the Companion payload. Delivery-profile
values override conflicting advanced values, explicit typed fields override the
profile, and the blueprint finally protects these correlation fields:

- `actions`
- `tag` when generated or explicitly supplied
- `action_data.modern_notifications_run_id`
- `action_data.modern_notifications_recipient_device_id`
- `action_data.modern_notifications_recipient_entity_id`

Example camera-independent image attachment:

```yaml
- action: script.modern_multi_device_notifications
  data:
    title: Front door
    message: Motion detected
    attachment_type: image
    attachment_url: /media/local/front-door/latest.jpg
```

Use `/media/local/` where possible so Home Assistant can supply authenticated
access to the Companion App.

## Response contract

Direct calls return a mapping with these keys:

| Key | Meaning |
| --- | --- |
| `status` | `sent`, `action`, `reply`, `timeout`, or `cleared` |
| `operation` | `send` or `clear` |
| `run_id` | Unique Home Assistant context ID for this invocation |
| `tag` | Effective notification tag |
| `action_key` | Caller-defined semantic key for the winning action |
| `action_slot` | `1`, `2`, or `3` |
| `reply_text` | Text supplied by a reply action |
| `responder_device_id` | Device ID echoed by the winning Companion callback |
| `recipients_attempted` | Notify entities for which a send was attempted |
| `recipients_unavailable` | Selected entities that could not resolve to a device |
| `callback_data` | Caller data echoed unchanged in the result |

An attempted send is not a delivery receipt. Home Assistant and the Companion
push service do not provide an end-to-end displayed-notification acknowledgment.

## Platform notes

- Android supports at most three notification actions, which defines this
  blueprint's cross-platform limit.
- Link actions use the Companion `URI` action. Android does not return an action
  event for these, so link-only notifications return immediately.
- Android notification-channel importance is largely fixed when a channel is
  first created. Changing the field later may not change an existing channel.
- Critical notifications require the relevant device permissions/settings.
- Clearing can be delayed or unavailable if the Companion App has not run
  recently on the target device.

## Development status

This is a from-scratch blueprint. It does not copy or preserve the public input
API of `samuelthng/t-house-blueprints/notifications.yaml`.
