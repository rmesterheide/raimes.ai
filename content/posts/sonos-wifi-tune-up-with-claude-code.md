---
title: "From 125 ms spikes to 1 ms: a Sonos and Wi-Fi tune-up with Claude Code"
date: 2026-10-18T20:27:23+02:00
draft: false
written_with_claude: true
cover:
  image: "/images/covers/sonos-wifi-tune-up-with-claude-code.jpg"
  alt: "From 125 ms spikes to 1 ms: a Sonos and Wi-Fi tune-up with Claude Code"
categories: ["homelab-ai"]
tags: ["homelab", "claude-code"]
summary: "Thirteen Sonos players, nine access points, one Sunday. The speakers were fine. The air was the problem: a soundbar stuck on 2.4 GHz, a mesh I never asked for, and access points jamming each other. What the measurements showed, the cable that made it worse, and the two settings that fixed it."
linkedin: ""
---

{{< tldr >}}
- The living room soundbar was the only Sonos player on 2.4 GHz, on the busiest channel in the house: 22 ms average, spikes of 125 ms. Every other player sat at 3 to 7 ms on 5 GHz. One Ethernet cable brought it to 1 ms.
- That cable silently moved six other players onto SonosNet, Sonos's own 2.4 GHz mesh, and they got worse (spikes up to 580 ms). Since May 2026 the Sonos app can switch SonosNet off for the whole household; wired and Wi-Fi players then mix cleanly. Sonos recommends exactly that for UniFi-style networks.
- The Wi-Fi was congesting itself: six of nine access points on 40 MHz in 2.4 GHz, five network names (SSIDs) on every radio, seven 5 GHz radios in one 80 MHz block. A fixed channel plan took 2.4 GHz from 40 to 91 % busy down to 15 to 22 %.
{{< /tldr >}}

I asked Claude Code one question on a Sunday afternoon: "check the latency between the Sonos speakers and suggest a better arrangement." Six hours later the house had a different network. Here is what it found, where I made it worse, and the two settings that mattered.

## Starting point

Thirteen Sonos players across two households on one UniFi network: a soundbar with a sub in the living room, a stereo pair in the attic office, four Era 100s, three old Play:3s, a One in the bathroom. Nine access points, four floors, concrete and brick. Everything on Wi-Fi, nothing wired, every channel on automatic. My feeling was "the living room hesitates when it is grouped with the kitchen". A feeling is not a measurement.

## What broke

Claude Code did not need the Sonos app. Every player answers HTTP on port 1400 with its room, model and a support page that lists its radio mode and channel; one SOAP call to any player returns the whole household, groups, coordinators and the band each player uses. Thirty pings per player from the wired Mac mini gave the latency. The survey took two minutes and produced three findings.

**The soundbar was the outlier.** The only player on 2.4 GHz, on channel 6, the channel our oldest access point had reported at 88 % utilisation weeks earlier. Average 22 ms, worst packet 125 ms. The sub rides on the soundbar's private link and inherited it: 28 ms, spikes of 126 ms. Everything else: 3 to 7 ms, worst packets 20 to 30 ms. Grouped audio flows from the player you start it on to every member, so every group with the living room crossed that link.

**Two access points in the same flat shared 5 GHz channel 40**, a few metres apart, and five players hung on one of them.

**Nobody could see this.** The UniFi controller knew which access point served which player and how strong the signal was, but the Mac mini that runs my daily checks had no working login, and the players' own diagnostics no longer expose signal strength.

## The cable that made it worse

The obvious fix was a cable to the soundbar. I plugged it in. The soundbar dropped to 1 ms. Good.

The next measurement showed six other players, the office pair, the three Play:3s and the bathroom One, had left 5 GHz. They were on SonosNet now, 2.4 GHz, channel 1. Sonos does this by design: the moment one SonosNet-capable player is wired, every other capable player joins the mesh; the Era 100s stayed on Wi-Fi only because they cannot do SonosNet. The office pair went from 3 ms to 7 to 11 ms. The Play:3s showed the spikes the soundbar used to have, 90 to 140 ms, one sample at 580 ms. On a 2.4 GHz band that was already full, the mesh had nowhere to go.

So I wired a second player in the office to give the mesh a second root. UniFi blocked the port within seconds: "Port blocked by STP to prevent a network loop." From the switch's point of view, two wired players plus the wireless mesh between them is a loop, and UniFi's Spanning Tree Protocol (STP) got there before Sonos's own could block a wireless link instead. Sonos's official advice for managed switches is a list of STP settings including a per-port path cost that UniFi does not expose. Forum threads from the last few years end the same way: wire exactly one player, or fight your switch.

## What fixed it

Claude Code went reading. The answer was six weeks old. Sonos app 85 (27 May 2026) added a household-wide "Disable SonosNet" switch, and a Sonos staff Q&A from June explains the purpose: wiring a player no longer flips the household onto the mesh, wired and Wi-Fi players can coexist, and it is aimed at exactly the UniFi scenario, because the mesh "could create extra network paths" back to the switches.

SonosNet off in the app, office cable pulled, soundbar stays wired. Two minutes later every player was back on 5 GHz except the soundbar on its cable, and the numbers were the best of the day.

Then the Wi-Fi. Reading the controller through my browser session, Claude Code found that automatic channel selection had put six of nine access points on 40 MHz in 2.4 GHz (each occupies two of the three usable channels), that all nine radios broadcast five network names (the beacons alone eat a large slice of 2.4 GHz airtime), and that seven of nine 5 GHz radios sat in the 36 to 48 block while the outdoor unit ran 160 MHz at 66 % busy. We drew a plan from the floor plan: 2.4 GHz on 20 MHz with fixed channels 1, 6 and 11 so that no two radios on the same floor or directly above each other share one, lower power where a radio has no clients, 5 GHz on 40 MHz with the two non-radar channels reserved for the two access points that carry most Sonos players. Minimum data rate on 2.4 GHz up to 6 Mbit/s, one unused network deleted, two legacy ones limited to the three access points that still have their devices. Claude Code applied the plan through the controller's API in one go; the radios came back within a minute.

![Sonos latency before and after](/images/sonos-wifi-tune-up/sonos-latency.svg)

![2.4 GHz utilisation per access point before and after](/images/sonos-wifi-tune-up/wifi-busy.svg)

| What | Before | After |
|---|---|---|
| Soundbar, average / worst packet | 22 ms / 125 ms | 1.0 ms / 1.4 ms |
| Sub | 28 ms / 126 ms | 2.3 ms / 6.5 ms |
| Slowest Wi-Fi player, average | 6.7 ms | 4.6 ms |
| 2.4 GHz busy, worst radio | 91 % | 22 % |
| 2.4 GHz busy, median radio | 47 % | 19 % |
| Outdoor 5 GHz busy | 66 % at 160 MHz | 15 % at 40 MHz |
| Packet loss | 0 % | 0 % |

Two players had parked themselves on 2.4 GHz during the radar check that new 5 GHz channels require; a power cycle sent them back. Since the next morning the daily report on the Mac mini checks every radio against the plan, flags any Sonos on 2.4 GHz, pings all players and appends one line per day to the network notes.

## Try it: read your Sonos players without the app

In a shell on any machine in the same network (macOS or Linux). Replace the address with one player's IP, which the Sonos app shows in that player's settings:

```bash
P=<player-ip>
curl -s "http://$P:1400/xml/device_description.xml" | grep -o -E '<roomName>[^<]*|<modelName>[^<]*'
curl -s "http://$P:1400/ZoneGroupTopology/Control" \
  -H 'Content-Type: text/xml; charset="utf-8"' \
  -H 'SOAPACTION: "urn:schemas-upnp-org:service:ZoneGroupTopology:1#GetZoneGroupState"' \
  --data '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body><u:GetZoneGroupState xmlns:u="urn:schemas-upnp-org:service:ZoneGroupTopology:1"/></s:Body></s:Envelope>' \
  | sed 's/&lt;/</g; s/&gt;/>/g; s/&quot;/"/g' \
  | grep -o -E 'ZoneName="[^"]*"|WirelessMode="[^"]*"|ChannelFreq="[^"]*"|Location="http://[0-9.]*'
ping -c 30 -i 0.2 -q $P | tail -1
```

Expected: the first line prints room and model. The second block prints, per player in the household, address, name, wireless mode (`1` Wi-Fi, `2` a sub or surround bonded to its soundbar, `0` wired or SonosNet) and the channel frequency (2412 to 2472 is 2.4 GHz, 5000 and above is 5 GHz). The ping line gives min, average, max and jitter. Anything on 2.4 GHz, or with an average above 15 ms or spikes above 60 ms, is where to look first.

## What I would do differently

- Measure before touching anything. The feeling pointed at the living room; the data said living room plus mesh plus channel plan.
- Wire one player, then switch SonosNet off, in that order. The app's wizard checks that every player reaches the router over Wi-Fi before it switches.
- Never leave nine access points on automatic channels. The automatic chose 40 MHz on 2.4 GHz and stacked 5 GHz into one block. A plan drawn from the floor plan took twenty minutes.
- Give the always-on machine a read-only login to the network controller before anything else. The hour without it was the least productive of the day.

Sources: Sonos, [In-app SonosNet setting](https://support.sonos.com/en/article/in-app-sonosnet-setting-how-to); Sonos staff, [Your SonosNet toggle questions, answered](https://en.community.sonos.com/product-updates/your-sonosnet-toggle-questions-answered-6934166) (June 2026); Sonos, [Configure STP settings to work with Sonos](https://support.sonos.com/en-us/article/configure-stp-settings-to-work-with-sonos); Sonos staff, [Sonos + UniFi best practices](https://en.community.sonos.com/tutorials-and-how-to-s-229149/sonos-unifi-best-practices-recommended-settings-6933597) (April 2026).
