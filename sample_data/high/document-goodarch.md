
# Azure Highly Available Web Application Architecture

This architecture illustrates a **multi-region deployment** pattern for resilient and scalable Azure Web Apps. It ensures business continuity and low latency by replicating services across two Azure regions, connected through Azure Front Door and protected by Web Application Firewall (WAF).

---

## 🧩 Components

### **Global Components**
- **Azure Front Door with WAF:** Provides global load balancing, SSL offloading, and application firewall protection.  
- **Microsoft Entra ID (Azure AD):** Centralized identity provider for authentication of both internal users and external customers.  
- **Firewall:** Protects inbound and outbound traffic from malicious access attempts.  

---

## 🌍 Regional Deployment Structure

Each region hosts an independent, but synchronized, **Web Apps Resource Group** containing all necessary components for running the application.

### **Region 1 - Web Apps Resource Group**
- **Web Apps (Web Front End):** Hosts the user-facing application, serving UI content.  
- **Web Apps (Web API):** Handles backend logic and connects to the database and cache.  
- **Application Insights:** Provides observability for logs, telemetry, and performance monitoring.  
- **App Configuration:** Centralized store for application settings and feature flags.  
- **Key Vault:** Manages secrets, certificates, and credentials securely.  
- **Azure Storage:** Supports static content, logs, and blob data.  
- **SQL Database:** Stores structured data for the web applications.  
- **Azure Cache for Redis:** Improves performance through caching of frequently accessed data.  
- **Virtual Network:** Contains subnets for isolation and security.  
  - **API App Service Subnet:** Hosts backend APIs.  
  - **Front-end App Service Subnet:** Hosts front-end applications.  
  - **Private Endpoint Subnet:** Connects securely to PaaS services like SQL and Storage.  
- **DNS Zones:** Manage internal and external domain name resolution.  

### **Region 2 - Web Apps Resource Group**
- Mirrors the Region 1 setup with:  
  - Web Apps (Front End & API)  
  - Application Insights  
  - App Configuration  
  - Key Vault  
  - Azure Storage  
  - SQL Database  
  - Azure Cache for Redis  
  - Virtual Network (with similar subnets)  
  - DNS Zones  
- Provides redundancy and failover capabilities in case Region 1 experiences an outage.  

---

## 🔄 Data Flows & Interactions

1. **User Authentication:**
   - **Call Center Users** and **Relcloud Customers** authenticate through **Microsoft Entra ID**.  
   - Authenticated sessions are routed via **Azure Front Door**.  

2. **Request Routing:**
   - **Azure Front Door** directs incoming traffic to the healthiest regional endpoint (Region 1 or Region 2).  
   - **WAF** filters requests and mitigates security threats before reaching the app.  

3. **Application Operation:**
   - Web Front End communicates with Web API through private VNet integration.  
   - Web API connects to **SQL Database** and **Redis Cache** for data persistence and caching.  
   - Configuration and secrets are fetched securely from **App Configuration** and **Key Vault**.  

4. **Data Replication:**
   - **SQL Database** replicates between regions to ensure data availability and consistency.  
   - **Azure Storage** can use geo-replication to maintain redundancy.  

5. **Monitoring and Diagnostics:**
   - **Application Insights** aggregates telemetry and performance metrics per region.  
   - Alerts are centralized for operational visibility.  

---

## 🧱 Technology Layers

| Layer | Components | Purpose |
|-------|-------------|----------|
| **Global Load Balancing & Security** | Azure Front Door, WAF, Firewall | Traffic routing, global availability, threat protection |
| **Identity & Access** | Microsoft Entra ID, Key Vault | Authentication, secret and certificate management |
| **Application** | Web Apps (Frontend, API), Azure Storage | Application hosting, static and dynamic content delivery |
| **Data** | SQL Database, Azure Cache for Redis | Data storage, replication, and caching |
| **Configuration & Monitoring** | App Configuration, Application Insights | Centralized configuration, performance analytics |
| **Networking** | Virtual Networks, Subnets, Private Endpoints, DNS Zones | Secure communication, name resolution, network isolation |

---

## ⚙️ High Availability Strategy

- **Active-Active Multi-Region Deployment:** Each region is fully capable of serving traffic.  
- **Automatic Failover:** Managed by **Azure Front Door**, directing requests to healthy endpoints.  
- **Data Replication:** Synchronous or asynchronous replication ensures resilience for databases and storage.  
- **Global Monitoring:** Unified telemetry via **Application Insights** for performance tracking and incident response.  

---

## 🛡️ Key Benefits

- High availability with multi-region failover.  
- Centralized security and authentication through Entra ID and WAF.  
- Scalable and resilient infrastructure for global workloads.  
- Secure internal networking using VNets and private endpoints.  
- Comprehensive observability and configuration management.  

---
