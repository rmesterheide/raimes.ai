---
title: "Route to Private AI Services 3.0, part 1 of 2: from a fresh ESX host to a Kubernetes API in one evening"
date: 2026-10-19T21:43:47+02:00
draft: false
written_with_claude: true
cover:
  image: "/images/covers/kubernetes-api-on-vsphere-in-one-evening.jpg"
  alt: "Route to Private AI Services 3.0, part 1 of 2: from a fresh ESX host to a Kubernetes API in one evening"
categories: ["vmware"]
tags: ["homelab"]
summary: "Part 1 of my route to Private AI Services 3.0 on vCenter alone: one host, one vCenter, no NSX. Within a few hours the platform for a lightweight, vCenter- and distributed-switch-only deployment was in place, and the vSphere Supervisor with the built-in Foundation Load Balancer answered as a Kubernetes API about seven minutes after the last click. What I prepared, what the wizard asks, and the five traps that cost me time."
linkedin: "https://www.linkedin.com/feed/update/urn:li:activity:7518036658362155008/"
linkedin: ""
---

I have installed ESX and vCenter by hand more times than I can count. DNS records, NTP, a distributed switch, a storage policy, then the long road to anything that looks like Kubernetes: an NSX Manager or an external load balancer, certificates, a second appliance to babysit. This evening was different. From a freshly installed ESX host to a Kubernetes API that answers on its own name took one evening, and the part I used to dread, the Supervisor activation, was the shortest step of all.

This is part 1 of 2 on my route to Private AI Services (PAIS) 3.0, deployed the lightweight way: vCenter and a vSphere Distributed Switch only, no NSX, no VMware Cloud Foundation (VCF) Automation. Within a few hours we had every platform prerequisite for that deployment in place: the Supervisor with its load balancer, the Kubernetes Service, the Local Consumption Interface in vCenter, a content library with Kubernetes releases, a namespace for PAIS and a registry appliance. Part 2 adds the GPU and PAIS itself.

![vSphere Client inventory at the end of the evening: cluster01 with the ESX host, the namespaces pais, svc-cci-ns, svc-tkg and svc-velero, the load balancer VM flb-sv01, the Supervisor control plane VM, vCenter and the registry appliance vis](/images/kubernetes-api-on-vsphere-in-one-evening/vcenter-inventory.png)
*The whole lab at the end of the evening: one host, one cluster, the Supervisor with one control plane VM and one load balancer VM, four namespaces, vCenter and a registry appliance.*

A disclosure: I work at Broadcom. This is my homelab and my own reading of public documentation, not an official statement.

{{< tldr >}}
- vSphere 9.1 activates a Kubernetes control plane, the **Supervisor**, straight from vCenter. With **vSphere Distributed Switch (VDS)** networking and the built-in **Foundation Load Balancer (FLB)** you need no NSX and no third-party load balancer.
- On one host it runs with **one control plane VM** and **one load balancer VM**. The API answered about **seven minutes** after "Finish", the Supervisor reported Running a few minutes later.
- The work is in the preparation: forward **and reverse** DNS, NTP, three port groups, a tag-based storage policy, HA and DRS on the cluster. Everything below is copy-paste ready.
- The traps were small and all of them were mine: a host still named `localdomain`, a DHCP pool sitting on top of the VIP range, a duplicate network name in the wizard, an SSH key type the host refuses, and a CLI that only ships for one CPU architecture.
{{< /tldr >}}

## The starting point

One AMD EPYC 7513 server with 512 GB RAM, local NVMe datastores, three 10 GbE ports. ESX 9.1.1 freshly installed, vCenter 9.1.1 deployed as a tiny appliance onto the same host, everything in an evaluation licence. A UniFi gateway does routing, DHCP and DNS for the house. No NSX Manager, no Avi, no extra appliances.

The goal: a Kubernetes API from which vSphere Kubernetes Service (VKS) clusters can be created, as the platform for PAIS in part 2.

## The network plan: three VLANs, one trunk port

The Supervisor needs three kinds of networks. On a single host I kept them as small as possible:

| Port group (on the VDS) | VLAN | Used for | Addresses (example) |
|---|---|---|---|
| `pg-mgmt` | 160 | Supervisor control plane, FLB management, ESX, vCenter | block of 5 for the Supervisor, 2 for the FLB |
| `pg-workload` | 162 | Supervisor and VKS cluster nodes | a static range of 100 |
| `pg-frontend` | 161 | Load balancer virtual IPs (VIPs) | 50 VIPs plus 10 FLB interface addresses |

The addresses in this post are examples (`172.16.160.0/24`, `.161`, `.162`), not my home network.

Two decisions made this simple:

1. **Tag only inside vSphere.** The distributed switch uplink (`vmnic2`) sits on a switch port that carries all VLANs tagged. The port groups set the VLAN ID; the physical switch needs no change per port group.
2. **No DHCP on the VIP and workload VLANs.** My gateway had DHCP enabled on both from an older lab, with a pool covering the whole subnet. Static ranges inside a DHCP pool work until the day they do not. Switch it off, or at least move the pool out of the way.

Before the wizard, check that nothing answers on the planned addresses and that the gateways do. On a Mac or Linux box:

```bash
# expect no "IN USE" lines, and 1 for each gateway
for ip in 172.16.160.{20..26} 172.16.161.{100,101,149,150,159} 172.16.162.{100,101,199}; do
  ping -c1 -t1 $ip >/dev/null 2>&1 && echo "IN USE $ip"
done
ping -c1 -t2 172.16.161.1 | grep -c "1 packets received"
ping -c1 -t2 172.16.162.1 | grep -c "1 packets received"
```

(`-t` is the timeout on macOS; on Linux use `-W`.)

## DNS: forward and reverse, before anything else

vCenter, the hosts and later the Supervisor API want names that resolve in both directions. I used local DNS records on the UniFi gateway under the domain `vcf.internal` (`.internal` is reserved for private use; `.local` collides with mDNS on Macs). Check both directions against the DNS server itself, not your laptop cache:

```bash
dig +short @<dns-server> esx01.vcf.internal     # expect the host IP
dig +short @<dns-server> -x <esx01-ip>         # expect esx01.vcf.internal.
```

Many small routers answer reverse lookups for their own host records automatically. Mine did, which saved me a second DNS server.

## Two host settings the installer does not get right for you

After setting a static address on the ESX console, the host still called itself `esx01.localdomain`. vCenter certificates and the Supervisor care about this. Fix it once over SSH:

```bash
# on the ESX host
esxcli system hostname set --fqdn=esx01.vcf.internal
esxcli network ip dns search remove --domain=localdomain
esxcli system hostname get | grep Fully       # Fully Qualified Domain Name: esx01.vcf.internal
```

NTP was off. My gateway does not answer NTP, so the host uses public pool servers:

```bash
esxcli system ntp set --server=0.de.pool.ntp.org --server=1.de.pool.ntp.org --server=2.de.pool.ntp.org --enabled=true
esxcli system ntp get | grep -E "Enabled|Servers"
```

`Time Synchronized` flips to true a few minutes later; `ntpq -p` on the host shows the peers in the meantime.

A side note that cost me three round trips: **the ESX SSH daemon runs in FIPS mode and refuses ed25519 keys.** The key was in `authorized_keys` and the login still failed with `Permission denied (publickey)`. An ECDSA key works:

```bash
# on your workstation
ssh-keygen -t ecdsa -b 256 -f ~/.ssh/id_ecdsa_vcf -C "vcf-lab"
cat ~/.ssh/id_ecdsa_vcf.pub | ssh root@esx01.vcf.internal 'cat >> /etc/ssh/keys-root/authorized_keys'
ssh -i ~/.ssh/id_ecdsa_vcf root@esx01.vcf.internal 'esxcli system security fips140 ssh get'   # Enabled: true
```

## The vCenter checklist: four things, ten minutes

The Supervisor Management start page lists the prerequisites itself. On a single host they boil down to this:

1. **Distributed switch with three port groups** (table above). VDS → Actions → Distributed Port Group → New, VLAN type "VLAN", one per role.
2. **A tag-based storage policy.** Without vSAN there is no default policy for the Supervisor. I created a tag category `k8s-storage` with a tag `supervisor`, put the tag on the NVMe datastore and created the VM storage policy `k8s-990pro` with "tag based placement". The storage compatibility page of the policy wizard should list exactly the datastore you meant.
3. **HA and DRS on the cluster.** DRS fully automated, HA on. With one host, set HA admission control to "Disabled", otherwise it reserves capacity for a failover that cannot happen.
4. **NTP and DNS settled** (above).

## The wizard, field by field

Supervisor Management → Get Started. These are the values that mattered:

| Step | Field | My value | Note |
|---|---|---|---|
| 1 | Networking stack / Load balancer | VDS / Foundation Load Balancer | Virtual Private Cloud (VPC) networking needs NSX; FLB is built in |
| 2 | Deployment | Cluster deployment, zone name `zone01` | the zone name cannot be changed later |
| 2 | Control plane high availability | off | one control plane VM; scaling to three later is supported |
| 3 | Storage policies | `k8s-990pro` for all three | control plane, ephemeral disks, image cache |
| 4 | Management network | static, `pg-mgmt`, block of 5 | one IP per control plane VM, a floating IP, a spare; cannot be changed after deployment |
| 5 | Workload network | static, `pg-workload`, range of 100, services CIDR `10.96.0.0/23` | with DHCP here you cannot add workload networks later |
| 6 | Load balancer | one-arm, size Medium, one VM | Small is labelled "POC only" (proof of concept) |
| 6 | FLB management | static, `pg-mgmt`, 2 addresses, **own network name** | see trap 3 |
| 6 | Virtual server network | `pg-frontend`, 10 interface IPs, 50 VIPs | the wizard pre-fills the workload network; "Assign" lets you pick a separate one |
| 7 | Control plane size / API server DNS name | Small / `sv01.vcf.internal` | the name ends up in the certificate |

The FLB sizes from the documentation, for planning:

| FLB size | vCPU | Memory |
|---|---|---|
| Small (POC only) | 2 | 4 GB |
| Medium | 4 | 8 GB |
| Large | 8 | 12 GB |
| Extra Large | 16 | 16 GB |

Then "Finish". I did not want to stare at a progress bar, so a small loop watched the rollout and stopped when the API answered:

```bash
# watch-sv01.sh: polls every 30 s until the Kubernetes API answers on a VIP
for i in {1..120}; do
  up=""; for ip in 172.16.160.{20..26}; do ping -c1 -t1 $ip >/dev/null 2>&1 && up="$up ${ip##*.}"; done
  api=""; for v in 172.16.161.{100..103}; do nc -z -G2 $v 6443 >/dev/null 2>&1 && api="$api $v"; done
  echo "$(date +%H:%M:%S) mgmt-up=[$up] api=[$api]"
  [[ -n $api ]] && exit 0
  sleep 30
done
```

The log tells the story: the first control plane address answered after three minutes, the FLB management address at minute seven, and in the same check the API on the first VIP. vCenter showed 8 of 9 conditions done shortly after and Running a few minutes later.

## Proof that it works

Point a DNS record for the API name at the first VIP (vCenter shows it as "Control Plane Node Address"), then check that the certificate on port 443 carries your name:

```bash
echo | openssl s_client -connect sv01.vcf.internal:443 -servername sv01.vcf.internal 2>/dev/null \
  | openssl x509 -noout -ext subjectAltName
# DNS:sv01.vcf.internal, IP Address:<vip>
```

Port 6443 shows the internal `kube-apiserver` certificate instead, and `/healthz` without a login answers 401. Both are expected.

The CLI tools come from the Supervisor itself. The download page at `https://sv01.vcf.internal/` builds its links in JavaScript; the plugin path is stable and has a checksum next to it:

```bash
# on a Mac (the plugin exists for darwin-amd64 only; Apple silicon needs Rosetta 2)
curl -sfk -o vsphere-plugin.zip https://sv01.vcf.internal/wcp/plugin/darwin-amd64/vsphere-plugin.zip
curl -sfk https://sv01.vcf.internal/wcp/plugin/darwin-amd64/sha256sum.txt
shasum -a 256 vsphere-plugin.zip          # must match the line above
unzip -o vsphere-plugin.zip && install -m 755 bin/kubectl-vsphere ~/.local/bin/
```

For `kubectl` itself I took a native arm64 build of the same minor version as the Supervisor (1.34):

```bash
kver=$(curl -sfL https://dl.k8s.io/release/stable-1.34.txt)
curl -sfLo kubectl https://dl.k8s.io/release/$kver/bin/darwin/arm64/kubectl
echo "$(curl -sfL https://dl.k8s.io/release/$kver/bin/darwin/arm64/kubectl.sha256)  kubectl" | shasum -a 256 -c
install -m 755 kubectl ~/.local/bin/
```

And the login:

```bash
kubectl vsphere login --server sv01.vcf.internal -u administrator@vsphere.local --insecure-skip-tls-verify
kubectl config get-contexts
```

```text
CURRENT   NAME                CLUSTER             AUTHINFO
*         sv01.vcf.internal   sv01.vcf.internal   wcp:sv01.vcf.internal:administrator@vsphere.local
          svc-cci-ns-xxxxx    sv01.vcf.internal   ...
          svc-tkg-xxxxx       sv01.vcf.internal   ...
          svc-velero-xxxxx    sv01.vcf.internal   ...
```

The three `svc-*` contexts are the namespaces of the core Supervisor Services that came along: the Kubernetes Service (VKS) 3.7.1, the Local Consumption Interface and the Velero operator. `--insecure-skip-tls-verify` is fine for the first evening; the clean way is to trust the vCenter certificate authority on the client.

## The next ten minutes: ready for the first cluster

To create VKS clusters, the Supervisor needs the Kubernetes release images. A subscribed content library with "download when needed" pulls only the metadata at first:

```bash
# the public library of VKS Kubernetes releases (VKr): check what it offers before you subscribe
curl -s https://wp-content.broadcom.com/v2/latest/items.json \
  | python3 -c 'import json,sys; [print(i["name"]) for i in json.load(sys.stdin)["items"] if "ubuntu-2404" in i["name"] and "v1.34" in i["name"]]'
```

Subscribe to `https://wp-content.broadcom.com/v2/latest/lib.json`, accept the certificate prompt, and then assign the library where the Kubernetes Service looks for it: **Supervisor → Configure → General → Kubernetes Service → Add**. The "Add Content Library" button on a namespace is for the VM Service and says so in small print. After that, a namespace with the storage policy and a few VM classes is all a first cluster needs.

## The five traps, in order of how much time they cost

1. **The SSH key type.** FIPS mode on the ESX SSH daemon rejects ed25519. Use ECDSA or RSA.
2. **`localdomain`.** The host had a static IP and a DNS server but still announced `esx01.localdomain`. Set the FQDN explicitly.
3. **Duplicate network names in the FLB step.** The FLB management network may sit on the same port group as the Supervisor management network, but the wizard rejects the same *name*. Call it `flb-mgmt`.
4. **DHCP on the VIP and workload VLANs.** Nothing broke, because I caught it before the wizard. It would have broken on the first lease that landed on a VIP.
5. **One CPU architecture.** `kubectl-vsphere` from the Supervisor is x86-only on macOS. On Apple silicon, install Rosetta 2 first. And the VCF CLI page on the Supervisor said "currently unavailable for download" for 9.1; the CLI and its plugin bundle for 9.1 come from the Broadcom Support Portal.

## What I would do differently

- **Write the IP plan before the first install,** including a dedicated block for the Supervisor and its load balancer. I re-planned twice because ESX and vCenter landed in a different network than first intended.
- **Set the API server DNS name in the wizard.** It costs one field and gives you a certificate with a real name.
- **Keep the watch loop.** Seven minutes are short when you see the addresses come up one after another, and long when you look at a spinner.

That closes part 1: every platform prerequisite for a vCenter- and distributed-switch-only PAIS deployment is in place, built in a few hours. Part 2 is PAIS 3.0 on this Supervisor: the service definition (and why the file with `-external` in its name is the right one without VCF Automation), the registry credentials, the GPU, and whether the Foundation Load Balancer is enough for it.
