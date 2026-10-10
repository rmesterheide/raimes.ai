---
title: "The voice box, measured: where two seconds really go, and the one-second trick that fixed the feeling"
date: 2026-10-10T08:30:00+02:00
draft: false
tags: ["private-ai", "homelab"]
summary: "Three days of timestamps on a Home Assistant voice assistant: cloud versus on-prem on one device, a local voice that ties with Azure in a blind test, a 4090 that finally earns its place, and a filler word in the firmware that changed nothing in the numbers and everything in the conversation."
---

**TL;DR**

- Home Assistant plays the answer only after the language model's last token. Streaming saves nothing; answer length and the model's total time are the only levers.
- Cloud speech recognition is faster than local Whisper after the last word (0.05 s vs. 0.4 s), because it transcribes while you talk. Local recognition buys privacy and proper names, not speed.
- The cloud voice never cost two seconds. Azure through Home Assistant: 0.38 s to first byte. The two seconds were the model finishing.
- A local Qwen3-TTS voice on the RTX 4090 delivers first audio in 0.11 s and ties with Azure in a blind listening test. Through Home Assistant it loses 0.3 s to an ffmpeg buffer.
- Two chains on one device: the kid's wake word goes to Claude Haiku 5.5 (right facts, keeps the rules, 1.8 s to first sound), the adults' wake word runs fully on-prem on the 4090 (0.9 to 1.3 s, 14B-grade answers).
- A one-second filler word ("Okay", "Hm, let me think") played from the device's own flash the moment you stop talking changed no measurement and fixed the feeling. Firmware snippet below.

Last time I promised a local voice. This is what happened when I measured instead of guessing, and it corrects two things I wrote in that post. The cloud voice does not cost two seconds. And the RTX 4090 that "stays off" is now the busiest machine in the house.

## Starting point

Same hardware: Home Assistant on a Raspberry Pi 5, a Home Assistant Voice Preview Edition on the kitchen shelf, an RTX 4090 workstation in the basement, a Mac mini that is always on. Same split: "Okay Nabu" is the kid's wake word, "Hey Jarvis" the adults'.

What changed is that every stage now has a number. Home Assistant stamps every pipeline event with a timestamp, and the websocket API hands them out (`assist_pipeline/pipeline_debug/get`). I also ran text-only pipelines per model, so the language model could be measured without a microphone, and I ran a proper benchmark on the voices: 90 German sentences, five repeats, at the engine and through Home Assistant, plus a Whisper round trip for intelligibility and a blind listening test. The first benchmark pass overlapped with other work on the GPU, so I ran it twice. Medians did not move; only the p99 did. All data, scripts and the corpus are in my homelab repo under `benchmarks/tts-voice`.

## What broke: my model of where the time goes

![Where the time goes](/images/voice-box-deep-dive/chain_breakdown.png)

After the last spoken word, four things happen in sequence.

1. **The box waits for silence**, about a second. Same for both chains, set to the most aggressive option the device offers.
2. **Speech-to-text.** The cloud needs 0.03 to 0.25 seconds, because it transcribes while you are still talking. Whisper large-v3-turbo on the 4090 needs 0.35 to 0.55, because it starts after you stop. So much for "local is faster".
3. **The language model until its last token.** Claude Haiku 5.5: 1.3 to 1.8 seconds. qwen3:14b on the 4090: 0.8 to 1.1.
4. **The handoff to the box**, a tenth of a second or two.

The detail that decides everything sits between 3 and 4: Home Assistant gives the box the audio only after the model's last token. The voice streams, the model streams, and playback still starts at the end. Time to first token is irrelevant. I had optimized for it anyway, and the stopwatch did not care. The levers that actually move the number are answer length and the model's total time.

The second thing that broke was my claim about the cloud voice. Measured from inside the LAN, Azure through Home Assistant Cloud delivers the first byte after 0.38 seconds (0.21 for short sentences), not two. The two seconds were the model finishing. I had blamed the wrong stage.

## What fixed it

**A local voice that ties with the cloud.** Qwen3-TTS 1.7B on the 4090, served over the Wyoming protocol, with a voice designed in three minutes from a text description ("a warm, friendly female voice around thirty, clear standard German, calm, like a kindergarten teacher explaining something to a five-year-old"). At the engine it produces first audio after 0.111 seconds with a p99 of 0.113 over 450 runs, and a real-time factor of 0.28. Piper is faster (0.08) and worse to understand (6.9 % word error rate in the Whisper round trip versus 3.9 %). Kokoro's German fine-tune on CPU cannot keep up with real time.

![Time to first audio by engine](/images/voice-box-deep-dive/ttfa_by_engine.png)

Through Home Assistant the local voice loses its head start: 0.45 seconds to first byte, constant, because HA converts the stream with ffmpeg and buffers 64 KiB before sending (core issue #184204, still open). Azure arrives as MP3 and skips that. So in the chain, the local voice is 0.07 seconds slower than the cloud one. I keep it anyway, and the blind test is why.

![Blind listening test](/images/voice-box-deep-dive/listening_test_mos.png)

Sixty clips, twelve sentences times five voices, loudness-normalized, shuffled, rated on the ITU-T P.800 five-point scale. Azure 4.33, Kokoro 4.25, Qwen3-TTS 4.17, Piper 4.08, Qwen3-TTS 0.6B 3.83, and every confidence interval overlaps every other. The evening before, listening to whole answers in the kitchen, I had called the local voice "better than Azure". Isolated sentences say: level. Level, and nothing leaves the house, and no subscription in the loop. That is enough. What the test did show clearly: both Qwen3 models mispronounce the name of our town, which a replacement list will fix, and the 0.6B model slips on names and dates.

**The 4090 earns its place.** It now runs the voice (5 GB of VRAM), Whisper as a Wyoming service (2.5 GB) and Ollama with qwen3:14b (10 GB). The 27B models do not fit next to the voice in 24 GB, which settled that debate. Two chains on one device:

| Stage | "Okay Nabu" (the kid) | "Hey Jarvis" (on-prem) |
|---|---|---|
| Speech-to-text | Azure via Home Assistant Cloud | Whisper on the 4090 |
| Answer | Claude Haiku 5.5, child system prompt, one short sentence | qwen3:14b via Ollama on the 4090 |
| Voice | Qwen3-TTS on the 4090 | the same |
| Last word to first sound | about 1.8 to 2.0 s | about 0.9 to 1.3 s |

The on-prem chain is a second faster and answers like a 14B model: "the Argentinosaurus was as big as a skyscraper", "there are infinitely many planets, like sand on the beach". The 8B model was worse. Haiku 5.5 gets the facts right, keeps the rule "hard questions go to Mum or Dad", and costs a third of Sonnet. For the child's wake word that is the trade I want. For the adults, the on-prem chain is the one that will keep working when the internet does not.

**The filler word.** Dialogue researchers call it a backchannel: the "mm-hm" that tells you the other side is still there. The box now plays a short "Okay" or "Hm, let me think", in the same voice it answers with, the instant it detects the end of your sentence, before anything is sent anywhere. A Home Assistant announcement cannot do this, it aborts the running pipeline, I checked. The ESPHome firmware has a hook for exactly that moment, and the device plays embedded sounds without touching the pipeline. Measured latency: unchanged. Perceived latency: the pause became a conversation. My five-year-old's verdict was one word, and it was not a complaint.

This is the overlay I added to the device's configuration in the ESPHome Device Builder add-on, under the official Nabu Casa package. The FLAC files are five short clips synthesized with the same voice, served from any web server on your LAN while the firmware compiles:

```yaml
# Appended to home-assistant-voice-<id>.yaml below the official package.
# Plays a random filler clip the moment the device detects end of speech.
audio_file:
  - id: filler_okay
    file: http://<your-lan-server>:8800/okay.flac
  - id: filler_hm
    file: http://<your-lan-server>:8800/mal_sehen.flac
  - id: filler_good_question
    file: http://<your-lan-server>:8800/gute_frage.flac

switch:
  - platform: template
    name: "Filler sound"
    id: filler_sound
    optimistic: true
    restore_mode: RESTORE_DEFAULT_ON
    entity_category: config

voice_assistant:
  on_stt_vad_end:
    - if:
        condition:
          switch.is_on: filler_sound
        then:
          - lambda: |-
              static const char* fillers[] = {"filler_okay", "filler_hm", "filler_good_question"};
              id(play_sound).execute(false, std::string(fillers[esp_random() % 3]));
```

Runs on the Voice PE after "Update" in the Device Builder; expect ten to twenty minutes of compile time on a Pi 5. Do not write `id: !extend va` on the `voice_assistant` block, the validator rejects it, and for single components ESPHome merges the lists anyway. The clips must be mono, 48 kHz, and the switch gives you an off button in Home Assistant.

## What broke on the way, none of it AI

- Home Assistant 2026.9.4 rejected Claude 5 models with thinking off and failed every follow-up question with thinking on (invalid thinking-block signature, because the replayed prefix had changed). 2026.10.0 fixed both; until then Sonnet 4.6 with thinking off was the workaround.
- A `{{ now() }}` template in the system prompt changed the prompt every minute and defeated Anthropic's prompt caching. Removing it brought the first token from 1.22 to 0.95 seconds. Home Assistant adds the time itself.
- Home Assistant caches synthesized speech by text, cloud and Wyoming alike, even with `cache: false`. Benchmarks and listening tests need fresh sentences or they measure a cache.
- PyAV 19 is incompatible with faster-whisper 1.2.1, and older PyAV wheels would not build on the box. One removed keyword argument in the library later, Whisper ran.
- The pipeline debug store keeps ten runs per pipeline. If you want a series, record the events yourself.

## What I would do differently

- **Instrument first, optimize second.** The timestamps were there all along; one websocket call would have saved me an evening of tuning the wrong stage.
- **Decide the voice with your ears and your values, not a leaderboard.** No public TTS ranking measures German naturalness, and my own blind test could not separate five voices. "Level and local" is a decision, not a measurement.
- **Give the GPU jobs that change the experience.** Voice, on-prem chain, filler word. Not speech recognition for the sake of it.
- **Keep the cloud where it is better than you can be at home**, which for me is the model that talks to my child.
- **Ask what the user is actually measuring.** My five-year-old does not time the first token. He waits for a sign of life. A one-second "Okay" from flash memory was worth more than every model swap on this list.

Next: a second rater for the listening test, a 30-run series per chain, and the adults' chain fully offline.
