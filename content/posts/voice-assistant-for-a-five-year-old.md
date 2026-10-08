---
title: "A voice assistant for a five-year-old, built on Home Assistant and Claude"
date: 2026-10-08T15:00:00+02:00
draft: true
tags: ["private-ai", "homelab", "claude-code"]
summary: "Two evenings from unboxing to a kid asking why the sky is blue. What was slow, what was wrong, and why the two expensive computers in the house ended up doing nothing."
---

My five-year-old asks a lot of questions. Dinosaurs, planets, pirates, how late it is. Alexa answers some of them, badly, and sends the rest to a search result nobody reads aloud. I wanted a box in the kitchen that answers like a patient adult, in German, in two short sentences, and that I control.

This is what I built in two evenings, what went wrong, and what I measured.

## The parts

- **Home Assistant Voice Preview Edition** as the microphone and speaker. Wake word detection runs on the device, it has echo cancellation and a hardware mute switch. A small Creative Pebble speaker hangs off the 3.5 mm jack because the built-in one is weak.
- **Home Assistant** on a Raspberry Pi 5 as the dispatcher. It owns the pipeline: wake word, speech-to-text, conversation agent, text-to-speech.
- **Claude** as the conversation agent, through the official Anthropic integration and an API key. Not through a subscription, more on that below.
- **Nabu Casa cloud** for speech recognition and the voice, for now.

Notice what is missing: the RTX 4090 workstation and the Mac mini that I had benchmarked for weeks as the future home of local speech recognition. They do nothing in this setup. That turned out to be the most useful finding.

## Evening one: it hears you, but not well

Setup was ten minutes. Home Assistant found the box as an ESPHome device, I picked the cloud pipeline and the wake word "Okay Nabu", and the first "what time is it" worked.

Then it felt bad. Sitting sixty centimetres from the box with the TV off, the wake word was ignored half the time, and when it did trigger, the beginning of my sentence was missing. The debug view in Home Assistant showed speech recognition at 0.02 to 0.14 seconds and intent matching under half a second. The pipeline was not the problem.

Three device settings were:

1. **Wake word sensitivity** ships as "slightly sensitive", the lowest setting. "Very sensitive" fixed the ignored wake words. No false triggers so far.
2. **The wake sound.** The confirmation beep plays while you are already talking, and the device drops your first word. Turning the beep off removed the missing sentence starts.
3. **Pause detection** on "aggressive" cuts the wait after your last word from over a second to about half a second.

The other failure was naming. My smart plugs were called things like `EZ-Mes`, which neither a human nor a speech model can say. Giving each entity a spoken alias ("Steckdose Esszimmer") made "switch off the dining room plug" work every time, locally, in 0.08 seconds, without any language model involved.

## Evening two: Claude joins, and breaks twice

The Anthropic integration adds a conversation agent to the pipeline. I gave it a German system prompt: family voice box, at most two short sentences, no lists, the listener is five, use comparisons from his world, send hard topics to Mum or Dad, never open the front door.

First question, "how big was a T. rex", came back with a bus-and-house comparison in two sentences. Exactly the tone I wanted. Then two things broke.

**Thinking blocks and follow-up questions.** With a Claude 5 model and extended thinking on, the first question works and the second fails with an API error about an invalid thinking-block signature. Home Assistant replays the conversation history on follow-ups, and the signatures no longer match. Setting thinking to "none" on a 5 model fails for a different reason: the integration sends the old parameter format. The fix for now is Claude Sonnet 4.6 with thinking off. Follow-ups work, answers take 1.6 seconds. This is a Home Assistant integration issue in Core 2026.9, not a model issue, and it will go away with an update.

**Everything went to Claude, including "switch off the plug".** With "prefer local command processing" on, Home Assistant matches sentence patterns first and only sends the rest to the model. Good in theory. In practice the model got 114 exposed entities as context on every call, local commands slowed from 0.08 to 1.6 seconds, and a misheard "make it dark in the dining room" produced a polite description of the lamp states instead of an action.

So I split it. **Two wake words, two personas.** The Voice PE supports a second wake word, and each wake word selects its own pipeline:

- "Okay Nabu" → the kid's pipeline. Claude only, no device control, no entities in the context, child-friendly system prompt.
- "Hey Jarvis" → the adults' pipeline. Home Assistant sentence patterns only, no language model, switches things in under 0.1 seconds.

No speaker recognition needed, which Home Assistant does not have anyway and which I would not want for a child's voice.

## Where the time goes

Measured from the last spoken word to the first word of the answer, kid's pipeline:

| Step | Time |
|---|---|
| Pause detection on the device | 0.5 to 1 s |
| Speech recognition (cloud) | 0.1 s |
| Claude Sonnet 4.6, thinking off | 1.6 s |
| Voice synthesis (cloud) and playback start | about 2 s |

Roughly four seconds for the kid, who talks slower, about 2.5 for an adult. Alexa manages about one. The two biggest items are the voice and the model, not recognition. Local Whisper on the 4090 would save 0.04 seconds per command. That is why the 4090 stays off.

Costs: with the system prompt cached, a question is about half a cent to one cent. Fifty questions a day is around ten euros a month. I set a spending cap in the Anthropic console before handing the box to the kid.

## What I would do differently

- **Fix the device settings before anything else.** Sensitivity, wake sound, pause detection. I spent an evening suspecting the pipeline when the defaults were the problem.
- **Aliases first, models later.** Most commands never need a language model if the entities have names people actually say.
- **Measure before buying hardware.** I ran a 2,259-clip Whisper benchmark on two machines to decide where recognition should run. The honest answer was: nowhere at home, for now. The cloud is faster and the privacy decision is separate from the speed decision.
- **Test the kid's questions before the kid does.** Death, scary things, swear words, "when is Christmas". The system prompt alone is not a filter.

Next on the list is a local voice. The cloud voice sounds great and costs two seconds. Piper on the Pi takes under half a second and sounds like 2015. Somewhere between the two there is a model that runs on the Mac mini, and that is the next measurement.
