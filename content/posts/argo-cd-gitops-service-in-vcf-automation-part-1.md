---
title: "GitOps for Private AI with VCF Automation, part 1: the ArgoCD service installed in three minutes"
date: 2026-11-24T13:29:39+01:00
draft: false
written_with_claude: true
cover:
  image: "/images/covers/argo-cd-gitops-service-in-vcf-automation-part-1.jpg"
  alt: "GitOps for Private AI with VCF Automation, part 1: the ArgoCD service installed in three minutes"
categories: ["vmware"]
tags: ["gitops", "argo-cd", "vcf-automation", "vks", "homelab"]
summary: "I installed the ArgoCD-based GitOps service of VMware Cloud Foundation Automation 9.1.1 in my lab: Software Depot, regional Harbor, the service itself, the new GitOps page in the organization portal and one attached Kubernetes cluster. Lab example: the install took over an ArgoCD Supervisor Service that was already running, and both instances and seven applications stayed healthy."
linkedin: "https://www.linkedin.com/feed/update/urn:li:activity:7530972972371681282/"
---

My lab already runs ArgoCD as a Supervisor Service. I installed it in vCenter, and I create instances with `kubectl`. VMware Cloud Foundation (VCF) Automation 9.1.1 offers a second way: a GitOps service that a provider installs once, and that organization users then use from their portal.

I wanted that second way for a catalog item that rolls out an NVIDIA NIM inference microservice through ArgoCD. The catalog of my lab organization shows what I am building toward: five items for private AI, and the NVIDIA NIM Endpoint is the one that ArgoCD rolls out.

![The catalog in the VCF Automation organization portal with five items: AI Kubernetes Cluster, AI Workstation, LLM Endpoint, NVIDIA NIM Endpoint and Triton Inference Server](/images/argo-cd-gitops-service-in-vcf-automation-part-1/catalog.webp)

This is part 1 of two. It covers the installation of the service and the first attached vSphere Kubernetes Service (VKS) cluster. Part 2 covers the catalog item.

The lab is the single-host VCF 9.1.1 fleet from the [build night post](/posts/single-host-vcf-fleet-build-night/).

**The status of the service.** Broadcom [introduced it as a Tech Preview in VCF 9.1.1](https://blogs.vmware.com/cloud-foundation/2026/09/03/from-bottleneck-to-breakthrough-centralizing-gitops-at-enterprise-scale-with-vcf-9-1-1/). With VCF 9.1.2, released on 24 November 2026, the service is generally available (GA), and the [release notes of VCF Automation 9.1.2](https://techdocs.broadcom.com/us/en/vmware-cis/vcf/vcf-9-0-and-later/9-1/release-notes/vmware-cloud-foundation-9-1-2-0-release-notes/vcf-automation-9-1-2-0-release-notes.html) list it under What's New. My lab still runs 9.1.1, so this post shows the Tech Preview version. The ArgoCD objects that part 2 uses also work with the ArgoCD Supervisor Service, which is installed through vCenter, and a section further down puts the two ways next to each other.

{{< tldr >}}
- **Six steps in this order:** fill the Software Depot of the fleet, install the regional Harbor, upload the ArgoCD package, install the ArgoCD Service, open the GitOps page in the organization portal, attach a cluster.
- **Harbor took about 10 minutes, the ArgoCD Service about 3 minutes.** Both are four-page dialogs under Service Management in the provider portal.
- **The lab example:** the install took over the ArgoCD Supervisor Service that was already running. Both existing instances and their seven applications stayed healthy, and the new GitOps page lists them.
- **An instance that existed before the install needs one role.** I assigned the role "ArgoCD Instance" to its service account, and the cluster was Ready 15 seconds later.
- **If you run VCF 9.1.2:** the service is generally available there, and the release notes say that 9.1.2 bundles it. I have not tested 9.1.2.
{{< /tldr >}}

## What the service needs

| Building block | Where | What it does here |
|---|---|---|
| Software Depot | fleet level, shown in VCF Operations | holds the packages and images of the services |
| Regional Harbor | VCF Automation, Service Management | serves those images to the Supervisor |
| ArgoCD Service | VCF Automation, Service Management | installs the ArgoCD operator on the Supervisors and adds the GitOps page |
| ArgoCD instance | a Supervisor namespace of the organization | the ArgoCD that a team works with |

Broadcom documents the installation in [Install Argo CD as VCF Service in VCF Automation](https://techdocs.broadcom.com/us/en/vmware-cis/vcf/vcf-service-administration-and-development/9-1/using-argo-cd-service/install-argocd-as--vcf-service-in-vcf-automation.html). That page starts with the download of the package. In my lab, two things had to happen before that package could be installed, so I start with them.

## Step 1: find the Software Depot of the fleet and fill it

The fleet has its own Software Depot service. VCF Operations shows it under Build > Software Depot, with its name and its connection. In my lab the depot is connected to an offline depot.

For that case, Broadcom describes one extra task in [Upload OCI Images When Software Depot Is in Offline Mode](https://techdocs.broadcom.com/us/en/vmware-cis/vcf/vcf-service-administration-and-development/9-1/managing-vsphere-kubernetes-service/deploying-vks-in-airgappen-environment/deploying-vks-with-vcf-or-vmware-vsphere-foundation/upload-oci-images-when-software-depot-is-in-offline-mode.html). The depot fetches most components on its own. The image bundles of services have to be uploaded with the VCF Download Tool.

I first asked the depot what it holds:

```bash
vcf-download-tool depot artifacts list \
  --vcf-version=9.1.1 \
  --depot-fqdn=<depot-fqdn> \
  --ops-fqdn=<vcf-operations-fqdn> \
  --ops-user=admin \
  --ops-user-password-file=<password-file>
```

`--depot-fqdn` is the name from the Software Depot page in VCF Operations. The tool logs in to VCF Operations and then talks to the depot.

The first run stopped and asked for the release manifest of the depot. So I uploaded the metadata first:

```bash
vcf-download-tool depot metadata upload \
  --depot-store=<depot-store> \
  --depot-fqdn=<depot-fqdn> \
  --ops-fqdn=<vcf-operations-fqdn> \
  --ops-user=admin \
  --ops-user-password-file=<password-file>
```

This was 2 MB and took 2 seconds. The command writes the release metadata of the fleet depot, so I ran it once and on purpose. After that, the list command worked and showed an empty list.

Then the three components:

```bash
for component in VCF_SERVICE_HARBOR SUPERVISOR_SERVICE_HARBOR VCF_SERVICE_ARGOCD; do
  vcf-download-tool depot artifacts upload \
    --depot-store=<depot-store> \
    --vcf-version=9.1.1 \
    --component=$component \
    --depot-fqdn=<depot-fqdn> \
    --ops-fqdn=<vcf-operations-fqdn> \
    --ops-user=admin \
    --ops-user-password-file=<password-file>
done
```

Each upload took between 21 and 26 seconds. The list then showed three components, each with an image count of 1/1.

I had started with two components, `VCF_SERVICE_HARBOR` and `VCF_SERVICE_ARGOCD`. The Harbor dialog in the next step names two bundles on its first page, the Harbor service of VCF Automation and the Harbor Supervisor Service. So I added `SUPERVISOR_SERVICE_HARBOR` before I went on. The [command reference of the VCF Download Tool](https://techdocs.broadcom.com/us/en/vmware-cis/vcf/vcf-9-0-and-later/9-1/lifecycle-management/binary-management-for-vmware-cloud-foundation/what-is-the-vcf-download-tool-/vcf-download-tool-sofware-depot-management-options.html) lists all depot commands.

## Step 2: install the regional Harbor

The regional Harbor is the registry from which the Supervisor pulls the images of its services. It caches what the Software Depot holds. Broadcom documents it in [Install Regional Harbor Through VCF Automation](https://techdocs.broadcom.com/us/en/vmware-cis/vcf/vcf-service-administration-and-development/9-1/using-harbor-as-vcf-service/using-harbor-as-a-vcf-service/install-harbor-through-vcf-automation.html). Two Broadcom knowledge base articles describe what an install of a Supervisor Service looks like when this Harbor is missing: [KB 447329](https://knowledge.broadcom.com/external/article/447329) and [KB 446977](https://knowledge.broadcom.com/external/article/446977).

The TechDocs page lists the prerequisites. I checked three of them before I opened the dialog:

- vCenter and the Supervisor run 9.1.0 or later.
- The Supervisor has an entry named `vcf-depot` under its Management Proxy configuration. In my lab the entry was there, created by the fleet, and it pointed at the depot from step 1.
- The storage class has room for the image cache.

The install is in the provider portal: Service Management > VCF Services > Harbor > Install. The dialog has four pages.

1. **Certificates.** Both bundles were shown as trusted. I accepted them.
2. **Select Deployment Scope.** I ticked the one region of the lab.
3. **Service Properties.** The page showed the region as "Ready to deploy", with the Supervisor and the storage class filled in. The YAML view shows the same values, plus the name and the certificate chain of the depot. I changed nothing.
4. **Review and Finalise.** The list of resources, among them the Harbor Supervisor Service, the proxy cache to the depot and the registry credentials for the Supervisor.

After Submit, the status went from Busy to Installing to Healthy. That took about 10 minutes.

![The Harbor service in Service Management after the install: status Healthy, labels Regional and System Managed, one region](/images/argo-cd-gitops-service-in-vcf-automation-part-1/harbor-general.webp)

![The first ten of twelve resources of the Harbor service: two secrets, the Harbor Supervisor Service, a user interface plugin, four overlays, the registry entry for the Supervisor and the depot endpoint. Every entry with a status shows Healthy](/images/argo-cd-gitops-service-in-vcf-automation-part-1/harbor-resources.webp)

The install changes the registry configuration of the Supervisor. During that time I watched one VKS cluster of my lab, which runs a model on a GPU worker node. Its control plane node was replaced once, about seven minutes after Submit. The worker node was not replaced while I watched, and the model on it answered every request. I would still plan a maintenance window for this step on a shared platform.

## Step 3: upload the ArgoCD package

With Harbor installed, the list of VCF services still had no entry for ArgoCD. The package has to be uploaded once in the provider portal. The TechDocs page for the service describes it:

1. Download the component `VCF_SERVICE_ARGOCD` with `vcf-download-tool artifacts download`. The result is one tar file.
2. In the provider portal, open Service Management > Partner Services, click Upload and select the tar file.
3. Wait until VCF Automation has resolved the file.

In my lab the file was 704 MB, and the package version was 1.3.0. About two minutes after the upload, the tab VCF Services showed a new card: ArgoCD Service, Not Installed.

The release notes of VCF Automation 9.1.2 say that 9.1.2 bundles version 1.2 of the service and that it can be upgraded to 1.3 through Service Management. So on 9.1.2 this upload may not be needed for a first install. I have not tested that.

## Step 4: install the ArgoCD Service

Before I clicked Install, I saved the state of what was running: the two `ArgoCD` objects, their applications, projects and targets, as JSON files. One instance belongs to a small agent platform in my lab and manages seven applications. The second one is empty and was waiting for part 2.

The dialog again has four pages.

1. **Certificates.** Four bundles, all trusted.
2. **Scope.** I left the default, "Deploy to all existing regions and newly created ones".
3. **Service Properties.** I changed nothing. One value to know for later: `keepCRDs` is `false` by default.
4. **Review and Finalise.** Nine resources: a secret, the Supervisor Service with the ArgoCD operator, two plugins for the user interface, two service accounts, a configuration handler, a role for the service, and a global role "ArgoCD Instance" for use in the organizations.

I clicked Submit and read the status after 8 seconds. It said Unhealthy with one installation error. The detail said that a service account was waiting for the role of the service and would try again after 30 seconds. I waited, and about 90 seconds after Submit the status was Installing. After about 3 minutes it was Healthy, with all nine components Healthy. The status settled after about 3 minutes, so I would wait that long before looking at single components.

![Service Management in the VCF Automation provider portal, tab VCF Services: the ArgoCD Service is listed under Installed with status Healthy, next to VKS cluster management and other services](/images/argo-cd-gitops-service-in-vcf-automation-part-1/service-management.png)

## The lab example: the running operator was taken over

This was the part I wanted to know before the install. A Supervisor Service with the same package name, `argocd-service.vsphere.vmware.com`, and the same version was already running on the Supervisor. I did not know whether the install would conflict with it.

The install did not conflict with it. This is what I measured:

| Time after Submit | What happened |
|---|---|
| 8 seconds | status Unhealthy, a service account waits for its role |
| about 90 seconds | status Installing |
| about 2 minutes | both `ArgoCD` objects go to `Progressing` |
| about 20 seconds later | both are `Ready` again |
| about 3 minutes | status Healthy, nine of nine components Healthy |

The row of the Supervisor Service in Service Management shows the build that I had installed in vCenter before. Both ArgoCD web interfaces answered with 200 during the whole time. The seven applications of the agent platform stayed Synced and Healthy.

In my lab, the VCF Automation integration could be added to a Supervisor Service that was already in use. The existing instances did not have to be created again. One role had to be assigned before a cluster could be attached, which is step 6.

## Step 5: the GitOps page in the organization portal

After a full reload, the organization portal has a new entry: Build & Deploy > Services > GitOps. The page is called Argo CD and has a button Create Argo CD Instance. Broadcom documents the dialog behind it in [Deploy an Argo CD Instance by Using the VCF Automation organization UI](https://techdocs.broadcom.com/us/en/vmware-cis/vcf/vcf-service-administration-and-development/9-1/using-argo-cd-service/managing-an-argo-cd-instance-and-resources-in-as-vcf-service-in--vcf-automation/deploy-an-argo-cd-instance-by-using-the--vcf-automation-provider-ui.html).

I did not create a new instance. The page already listed both existing ones, each with status Success, its project and its creation date.

![The instance list on the GitOps page: two ArgoCD instances with status Success in the same project](/images/argo-cd-gitops-service-in-vcf-automation-part-1/gitops-instances.png)

An instance opens with four tabs: Argo CD Instance Details, User Access, Resources and Scope. The details show a service account in VCF Automation that belongs to the instance.

## Step 6: attach a VKS cluster

The Scope tab has two buttons, Attach Namespace and Attach Kubernetes Cluster. I attached the VKS cluster that part 2 will deploy to: region, project, cluster, Attach. Broadcom documents this in [Manage a VKS Cluster in Argo CD by Using the VCF Automation organization UI](https://techdocs.broadcom.com/us/en/vmware-cis/vcf/vcf-service-administration-and-development/9-1/using-argo-cd-service/managing-an-argo-cd-instance-and-resources-in-as-vcf-service-in--vcf-automation/manage-resources-in-vsphere-namespaces-with-argo-cd/manage-a-vks-cluster-in-argo-cd-by-using-the-vcf-automation-organization-ui.html).

The new row showed Pending. Behind the row is a `ManagedEntity` object in the namespace of the instance, the same kind of object I write by hand for the Supervisor Service. Its conditions name the reason:

```bash
kubectl -n <instance-namespace> get managedentity <name> \
  -o jsonpath='{range .status.conditions[*]}{.type}{"\t"}{.status}{"\t"}{.message}{"\n"}{end}'
```

```text
ArgoCDExists               True
VCFAutomationAccessValid   False   ... Insufficient privileges (HTTP 403): Please verify that
                                   the VCF Automation service account has been assigned the
                                   required role in VCF Automation
```

The service account of the instance needs the role "ArgoCD Instance". The hint next to the service account in the portal says that the account gets this role automatically. My instance existed before the service was installed, so I assigned the role myself. The page [Deploying an Argo CD Instance](https://techdocs.broadcom.com/us/en/vmware-cis/vcf/vcf-service-administration-and-development/9-1/using-argo-cd-service/deploying-an-argo-cd-instance.html) describes this binding as a manual step.

In the organization portal: Administer > Access Control > Service Accounts. The list showed one account per ArgoCD instance, both active. I opened Edit on the account of my instance, typed "Argo" into Assign Role, selected "ArgoCD Instance" and saved.

The cluster was Ready 15 seconds later:

```text
VCFAutomationAccessValid   True   VCF Automation access verified and all required permissions are granted
ClusterInfoFetched         True   Cluster info fetched from VCF Automation API
RegionValid                True
SecretReady                True   ArgoCD cluster secret ready
```

The status of the object now carries the API address of the cluster and the name of a cluster secret. An ArgoCD `Application` uses one of the two as its destination. I gave the role only to the account of this instance. The instance of the agent platform keeps working as before, with the targets it already had.

## Two ways to the same objects

Both ways use the same operator and the same objects: `ArgoCD` for an instance, `ManagedEntity` for a target, `Application` for what gets deployed. The TechDocs page [Deploying an Argo CD Instance](https://techdocs.broadcom.com/us/en/vmware-cis/vcf/vcf-service-administration-and-development/9-1/using-argo-cd-service/deploying-an-argo-cd-instance.html) calls them two deployment modes and compares them. This table follows that comparison and adds my lab in the last row.

| | ArgoCD Supervisor Service | ArgoCD Service in VCF Automation |
|---|---|---|
| Status | supported for production | Tech Preview in 9.1.1, generally available with 9.1.2 |
| Installed by | a vSphere administrator, in vCenter, per Supervisor | a provider administrator, in Service Management, for all Supervisors of the selected regions |
| Meant for | vSphere environments without VCF Automation | environments with several organizations that VCF Automation manages |
| An instance is created | with `kubectl` or the VCF command line, as an `ArgoCD` object | on the GitOps page of the organization portal, also with the command line |
| Login to ArgoCD | local account, single sign-on configured by hand | single sign-on with the VCF Automation login by default |
| Identity of the instance | a Kubernetes service account in the namespace | a service account in VCF Automation |
| Access to a target | a RoleBinding for that service account in the target namespace | the role "ArgoCD Instance" for the service account in VCF Automation |
| A cluster is attached | with a `ManagedEntity` manifest | on the Scope tab, which creates the `ManagedEntity` |
| In my lab | the agent platform, seven applications, since 21 November | the instance for part 2, created before the install, with one cluster attached on the Scope tab on 24 November |

The agent platform in my lab runs entirely on the Supervisor Service. If you run vSphere without VCF Automation, you can build what part 2 shows with the Supervisor Service as well. The manifests are the same. The differences are who creates the instance and how it gets access to a target.

## What I build next

- **Part 2:** an NVIDIA NIM as a catalog item. The order creates an ArgoCD application, ArgoCD rolls out the NIM on the attached cluster, and the model becomes available at the gateway of Private AI Services.
- **A deep learning VM through ArgoCD,** as its own post.
- **A new instance from the GitOps page,** to see the automatic role assignment and the single sign-on.
- **The same steps as an organization user** without administrator rights.
- **Upgrade and uninstall.** I want to read how both work now that Service Management has installed the service, and what `keepCRDs` means for the instances.

## Documentation and further reading

- Broadcom: [Installing and Configuring the Argo CD Service in VCF and vSphere](https://techdocs.broadcom.com/us/en/vmware-cis/vcf/vcf-service-administration-and-development/9-1/using-argo-cd-service.html)
- Broadcom: [Install Argo CD as VCF Service in VCF Automation](https://techdocs.broadcom.com/us/en/vmware-cis/vcf/vcf-service-administration-and-development/9-1/using-argo-cd-service/install-argocd-as--vcf-service-in-vcf-automation.html)
- Broadcom: [Install the VMware Argo CD Operator as a Supervisor Service](https://techdocs.broadcom.com/us/en/vmware-cis/vcf/vcf-service-administration-and-development/9-1/using-argo-cd-service/install-argo-cd-service.html)
- Broadcom: [Deploying an Argo CD Instance](https://techdocs.broadcom.com/us/en/vmware-cis/vcf/vcf-service-administration-and-development/9-1/using-argo-cd-service/deploying-an-argo-cd-instance.html)
- Broadcom: [Deploy an Argo CD Instance by Using the VCF Automation organization UI](https://techdocs.broadcom.com/us/en/vmware-cis/vcf/vcf-service-administration-and-development/9-1/using-argo-cd-service/managing-an-argo-cd-instance-and-resources-in-as-vcf-service-in--vcf-automation/deploy-an-argo-cd-instance-by-using-the--vcf-automation-provider-ui.html)
- Broadcom: [Manage a VKS Cluster in Argo CD by Using the VCF Automation organization UI](https://techdocs.broadcom.com/us/en/vmware-cis/vcf/vcf-service-administration-and-development/9-1/using-argo-cd-service/managing-an-argo-cd-instance-and-resources-in-as-vcf-service-in--vcf-automation/manage-resources-in-vsphere-namespaces-with-argo-cd/manage-a-vks-cluster-in-argo-cd-by-using-the-vcf-automation-organization-ui.html)
- Broadcom: [Install Regional Harbor Through VCF Automation](https://techdocs.broadcom.com/us/en/vmware-cis/vcf/vcf-service-administration-and-development/9-1/using-harbor-as-vcf-service/using-harbor-as-a-vcf-service/install-harbor-through-vcf-automation.html)
- Broadcom: [Upload a Partner Service to Your VCF Automation Provider Management UI](https://techdocs.broadcom.com/us/en/vmware-cis/vcf/vcf-service-administration-and-development/9-1/using-solution-add-ons/upload-a-solution-add-on.html)
- Broadcom: [Upload OCI Images When Software Depot Is in Offline Mode](https://techdocs.broadcom.com/us/en/vmware-cis/vcf/vcf-service-administration-and-development/9-1/managing-vsphere-kubernetes-service/deploying-vks-in-airgappen-environment/deploying-vks-with-vcf-or-vmware-vsphere-foundation/upload-oci-images-when-software-depot-is-in-offline-mode.html)
- Broadcom: [VCF Download Tool Software Depot Management Options](https://techdocs.broadcom.com/us/en/vmware-cis/vcf/vcf-9-0-and-later/9-1/lifecycle-management/binary-management-for-vmware-cloud-foundation/what-is-the-vcf-download-tool-/vcf-download-tool-sofware-depot-management-options.html)
- Broadcom: [VCF Automation 9.1.2.0 Release Notes](https://techdocs.broadcom.com/us/en/vmware-cis/vcf/vcf-9-0-and-later/9-1/release-notes/vmware-cloud-foundation-9-1-2-0-release-notes/vcf-automation-9-1-2-0-release-notes.html)
- Broadcom knowledge base: [Error: Missing depot service when installing Supervisor Services in VCF 9.1](https://knowledge.broadcom.com/external/article/447329) and [Supervisor Services Installation Fails: Cannot Reach VCF Software Depot](https://knowledge.broadcom.com/external/article/446977)
- VMware Cloud Foundation blog: [From Bottleneck to Breakthrough: Centralizing GitOps at Enterprise Scale with VCF 9.1.1](https://blogs.vmware.com/cloud-foundation/2026/09/03/from-bottleneck-to-breakthrough-centralizing-gitops-at-enterprise-scale-with-vcf-9-1-1/)
- vSphere Supervisor Services: [ArgoCD Service v1.3.0 Release Notes](https://vsphere-tmm.github.io/Supervisor-Services/argocd-service/release-notes-v1.3.0.html)
- William Lam: [VCF 9.1.1 - Single ESX Host for VCF Fleet, VCF Workload Domain or VCF Cluster](https://williamlam.com/2026/09/vcf-9-1-1-single-esx-host-for-vcf-fleet-vcf-workload-domain-or-vcf-cluster.html), the guide my lab is built along
