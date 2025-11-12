
# Azure Architecture Overview

This architecture implements a **hub-and-spoke model** integrating Azure Kubernetes Service (AKS) with secure networking, private endpoints, ingress management, and monitoring. It provides a scalable, secure, and observable environment for containerized workloads.

---

## 🧩 Components

### **Hub Virtual Network**
- **Azure Firewall Subnet (Outbound):** Manages outbound traffic and enforces security policies.  
- **Azure Bastion Subnet (Management):** Provides secure SSH/RDP access to Azure resources without exposing public IPs.  
- **Gateway Subnet (To On-Premises):** Connects to the on-premises network via VPN or ExpressRoute gateway.  

### **Spoke Virtual Network**
- **Private Link Endpoints Subnet:** Hosts private endpoints for secure access to Azure services (e.g., Key Vault, ACR).  
- **Ingress Resources Subnet:** Contains an **internal load balancer** for routing internal traffic into the AKS cluster.  
- **Azure Application Gateway Subnet:** Hosts the **Application Gateway** that manages external HTTP/HTTPS traffic from the Internet.  
- **Cluster Nodes Subnet:** Houses the **AKS cluster** with separate system and user node pools.  

### **Azure Kubernetes Service (AKS)**
- **System Node Pool:** Runs cluster-level services such as system add-ons.  
- **User Node Pool:** Hosts application workloads and ingress controllers (e.g., Traefik).  
- **Traefik Ingress Controller:** Manages routing within the cluster and integrates with the Application Gateway.  

### **Supporting Services**
- **Azure Key Vault:** Securely stores secrets, keys, and certificates accessed by workloads.  
- **Azure Container Registry (ACR):** Stores and manages container images pulled by AKS.  
- **Azure Monitor Workspace:** Aggregates metrics, logs, and telemetry via **Managed Prometheus** and other monitoring services.  

### **External Connectivity**
- **On-Premises Network:** Connects to Azure through the Gateway subnet.  
- **Spoke (Remote Office):** Communicates with the hub network via virtual network peering.  
- **Internet:** Provides external access to public endpoints through the Application Gateway.  

---

## 🔄 Data Flows & Interactions

1. **Ingress (External → Internal):**
   - Traffic enters from the **Internet** through the **Azure Application Gateway**.  
   - The gateway forwards requests to the **internal load balancer** in the ingress subnet.  
   - Requests are routed to the appropriate **AKS workloads** via the **Traefik ingress controller**.  

2. **Outbound Communication:**
   - Outbound requests from workloads pass through the **Azure Firewall** for security and compliance.  
   - The firewall manages NAT and outbound rule enforcement.  

3. **Private Access to Azure Services:**
   - AKS and other components use **Private Link Endpoints** to securely connect to **Azure Key Vault** and **ACR** without traversing the public Internet.  

4. **On-Premises Integration:**
   - Connectivity between Azure and on-premises systems is maintained through the **Gateway subnet**, enabling hybrid workloads or data synchronization.  

5. **Monitoring and Observability:**
   - Logs and metrics from AKS and network components are sent to **Azure Monitor** and **Managed Prometheus** for centralized observability and alerting.  

---

## 🧱 Technology Layers

| Layer | Components | Purpose |
|-------|-------------|----------|
| **Networking** | Virtual Networks, Subnets, Firewall, Bastion, Gateway, VNet Peering | Isolation, secure connectivity, hybrid access |
| **Compute** | Azure Kubernetes Service (System & User Node Pools) | Container orchestration, workload execution |
| **Ingress / Egress** | Application Gateway, Internal Load Balancer, Traefik | Traffic routing, load balancing, ingress control |
| **Security** | Azure Firewall, Key Vault, Private Link Endpoints | Policy enforcement, secret management, private access |
| **Storage & Registry** | Azure Container Registry | Container image management |
| **Monitoring** | Azure Monitor, Managed Prometheus | Observability, metrics, logging, and health insights |

---
