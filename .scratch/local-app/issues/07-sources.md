# Sources for segowl/defaults/port_labels.csv

Vendor documentation, IETF RFCs and the IANA registry only; nothing taken from nmap-services.
[checked] = page fetched and port values compared during this ticket. All other URLs are the vendor's reference pages, not re-fetched one by one: check them when reviewing the PR.

## Standard protocols
- Rows tagged "(RFC NNNN)" in the product column → https://www.rfc-editor.org/rfc/rfcNNNN (the RFC named on the row)
- Other standard ports (rsync, AFP, r-services, X11 6000-6063, OpenVPN, WireGuard, SSDP, NetFlow 2055, sFlow, Oracle 2483/2484, NDMP) → https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml
- IPMI RMCP udp:623 → https://www.intel.com/content/www/us/en/products/docs/servers/ipmi/ipmi-second-gen-interface-spec-v2-rev1-1.html

## Microsoft
- Windows / AD service ports (RPC 135, 49152-65535, SMB, NetBIOS, GC 3268/3269, ADWS 9389, KMS 1688, WinRM, LLMNR, RDP, RD Gateway, WDS/PXE, AD FS 49443) → https://learn.microsoft.com/en-us/troubleshoot/windows-server/networking/service-overview-and-network-port-requirements
- WinRM 5985/5986 → https://learn.microsoft.com/en-us/windows/win32/winrm/installation-and-configuration-for-windows-remote-management
- Hyper-V VMConnect 2179, live migration 6600 → https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/plan/plan-for-hyper-v-networking-in-windows-server
- Configuration Manager 2701, 10123 → https://learn.microsoft.com/en-us/mem/configmgr/core/plan-design/hierarchy/ports
- WSUS 8530/8531 → https://learn.microsoft.com/en-us/windows-server/administration/windows-server-update-services/deploy/2-configure-wsus
- SQL Server 1433, udp:1434, 4022, 5022 → https://learn.microsoft.com/en-us/sql/sql-server/install/configure-the-windows-firewall-to-allow-sql-server-access

## Out-of-band
- HPE iLO 443, 17988, 17990, 3002 → https://support.hpe.com/hpesc/public/docDisplay?docId=a00105236en_us (iLO 5 User Guide, "iLO network port configuration options")
- Dell iDRAC 443, 5900, 3668 → https://www.dell.com/support/manuals/en-us/idrac9-lifecycle-controller-v7.x-series/idrac9_7.xx_ug/idrac-port-information
- Supermicro BMC 5120, 5123, 5900 → https://www.supermicro.com/manuals/other/BMC_Users_Guide_X12_H12.pdf
- Lenovo XClarity Controller 3900 → https://pubs.lenovo.com/xcc/ports
- Cisco IMC 2068 → https://www.cisco.com/c/en/us/td/docs/unified_computing/ucs/c/sw/gui/config/guide/4_1/b_Cisco_UCS_C-series_GUI_Configuration_Guide_41.html

## Virtualization
- VMware ESXi / vCenter / Horizon (443, 902, 427, 5989, 8000, 8182, 5480, 9443, 7444, 6501/6502, 4172, 8443, 22443) → https://ports.broadcom.com/
- Proxmox VE 8006, 3128, 5900-5999, udp:5405-5412, 60000-60050 [checked] → https://pve.proxmox.com/pve-docs/chapter-pve-firewall.html
- Proxmox Backup Server 8007 → https://pbs.proxmox.com/docs/installation.html
- Nutanix Prism 9440 → https://portal.nutanix.com/page/documents/list?type=software&filterKey=software&filterVal=Ports%20and%20Protocols
- libvirt 16509/16514 → https://libvirt.org/remote.html
- Citrix ICA 1494, CGP 2598 → https://docs.citrix.com/en-us/tech-zone/build/tech-papers/citrix-communication-ports.html

## Backup and storage
- Veeam B&R v13 (9419, 9420, 10443, 6160, 6161, 6162, 2500-3300, 6170) [checked] → https://helpcenter.veeam.com/docs/vbr/userguide/used_ports.html
- Veeam B&R v12 (9392, 9396, 9401, 9394) [checked] → https://helpcenter.veeam.com/docs/backup/vsphere/used_ports.html?ver=120
- Veeam Backup Enterprise Manager 9443 → https://helpcenter.veeam.com/docs/backup/em/em_used_ports.html
- Commvault 8400, 8401, 8403 → https://documentation.commvault.com/2024e/essential/default_port_numbers.html
- Veritas NetBackup 1556, 13724, 13782 → https://www.veritas.com/support/en_US/doc/18716246-126559472-0/v40740069-126559472
- Veritas Backup Exec 6101, 10000 → https://www.veritas.com/support/en_US/doc/59226269-127535535-0/v65015099-127535535
- Bacula / Bareos 9101-9103 → https://www.bacula.org/15.0.x-manuals/en/main/Customizing_Configuration_Files.html
- IBM Storage Protect 1500, 1581 → https://www.ibm.com/docs/en/storage-protect/8.1.23?topic=communication-tcpip-ports
- Acronis Cyber Protect 9877 → https://www.acronis.com/en-us/support/documentation/AcronisCyberProtect_16/#network-ports.html
- NetApp ONTAP SnapMirror 11104/11105 → https://docs.netapp.com/us-en/ontap/networking/ontap_internal_ports.html
- Dell Data Domain 2051 → https://www.dell.com/support/kbdoc/en-us/000037046
- Synology DSM 5000/5001 → https://kb.synology.com/en-global/DSM/tutorial/What_network_ports_are_used_by_Synology_services
- QNAP QTS 8080 → https://www.qnap.com/en/how-to/faq/article/what-is-the-port-number-used-by-the-qnap-nas
- Ceph 3300, 6789, 6800-7300 → https://docs.ceph.com/en/latest/rados/configuration/network-config-ref/
- GlusterFS 24007 → https://docs.gluster.org/en/latest/Install-Guide/Install/
- MinIO 9000/9001 → https://min.io/docs/minio/linux/reference/minio-server/minio-server.html

## Network and security appliances
- Fortinet FortiGate / FortiManager / FortiAnalyzer / EMS (443, 541, 514, 1000, 1003, 8013, 10443, 8008) → https://docs.fortinet.com/document/fortigate/7.4.0/fortinet-communication-ports-and-protocols/303168/fortigate-open-ports
- Palo Alto PAN-OS management (443, 4443, 6080-6082) [checked] → https://docs.paloaltonetworks.com/pan-os/11-1/pan-os-admin/firewall-administration/reference-port-number-usage/ports-used-for-management-functions
- Palo Alto Panorama 3978, 28443 → https://docs.paloaltonetworks.com/pan-os/11-1/pan-os-admin/firewall-administration/reference-port-number-usage/ports-used-for-panorama
- Palo Alto HA 28769, 28260 → https://docs.paloaltonetworks.com/pan-os/11-1/pan-os-admin/firewall-administration/reference-port-number-usage/ports-used-for-ha
- Palo Alto User-ID 5007, GlobalProtect udp:4501 → https://docs.paloaltonetworks.com/pan-os/11-1/pan-os-admin/firewall-administration/reference-port-number-usage/ports-used-for-user-id and .../ports-used-for-globalprotect
- Cisco Smart Install 4786 → https://sec.cloudapps.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-20180328-smi2
- Cisco Secure Firewall FMC 8305 → https://www.cisco.com/c/en/us/td/docs/security/secure-firewall/management-center/admin/740/management-center-admin-74/system-security-requirements.html
- Cisco ISE 8443, 8905, 8910, udp:1645/1646 → https://www.cisco.com/c/en/us/td/docs/security/ise/3-3/install_guide/b_ise_installationGuide33/b_ise_InstallationGuide33_chapter_6.html
- Check Point 256, 257, 18190-18192, 18264 → https://support.checkpoint.com/results/sk/sk52421
- Sophos Firewall 4444 → https://docs.sophos.com/nsg/sophos-firewall/latest/Help/en-us/webhelp/onlinehelp/AdministratorHelp/SystemServices/Ports/
- MikroTik Winbox 8291, API 8728/8729, MNDP udp:5678 → https://help.mikrotik.com/docs/display/ROS/Services
- F5 BIG-IP 4353, udp:1026, 8443 → https://my.f5.com/manage/s/article/K000137353
- Ubiquiti UniFi 8443, 8080, udp:3478, udp:10001 → https://help.ui.com/hc/en-us/articles/218506997
- HPE Aruba 4343, udp:8211 → https://www.arubanetworks.com/techdocs/ArubaOS_8.10.0.0_Web_Help/Content/arubaos-solutions/firewall-roles/netw-port-firewall.htm

## Databases and caches
- Oracle Database 1521, Connection Manager 1830 → https://docs.oracle.com/en/database/oracle/oracle-database/19/ladbi/oracle-database-default-ports.html
- MySQL 3306, 33060 → https://dev.mysql.com/doc/mysql-port-reference/en/mysql-ports-reference-tables.html
- PostgreSQL 5432 → https://www.postgresql.org/docs/current/runtime-config-connection.html
- SAP ASE 5000 → https://help.sap.com/docs/SAP_ASE
- IBM Db2 50000 → https://www.ibm.com/docs/en/db2/11.5?topic=ports-default
- Firebird 3050 → https://firebirdsql.org/file/documentation/html/en/firebirddocs/qsg5/firebird-5-quickstartguide.html
- MongoDB 27017 → https://www.mongodb.com/docs/manual/reference/default-mongodb-port/
- Redis 6379, Sentinel 26379 → https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/
- Memcached 11211 → https://github.com/memcached/memcached/wiki/ConfiguringServer
- Apache Cassandra 9042, 7000, 7001, 7199 → https://cassandra.apache.org/doc/latest/cassandra/managing/configuration/cass_yaml_file.html
- Elasticsearch 9200/9300 → https://www.elastic.co/guide/en/elasticsearch/reference/current/modules-network.html
- CouchDB 5984 → https://docs.couchdb.org/en/stable/setup/cluster.html
- Couchbase 8091 → https://docs.couchbase.com/server/current/install/install-ports.html
- InfluxDB 8086 → https://docs.influxdata.com/influxdb/v2/reference/config-options/
- ClickHouse 8123, 9000 → https://clickhouse.com/docs/en/guides/sre/network-ports
- Neo4j 7474, 7687 → https://neo4j.com/docs/operations-manual/current/configuration/ports/
- CockroachDB 26257 → https://www.cockroachlabs.com/docs/stable/cockroach-start
- SAP NetWeaver 32NN/33NN/36NN, HANA 3NN13/3NN15 → https://help.sap.com/docs/Security/575a9f0e56f34c6e8138439eefc32b16/616a3c0b1cc748238de9c0341b15c63c.html

## Web and application servers
- Apache Tomcat 8080, 8009, 8005 → https://tomcat.apache.org/tomcat-10.1-doc/config/server.html
- Oracle WebLogic 7001/7002 → https://docs.oracle.com/en/middleware/fusion-middleware/weblogic-server/14.1.1.0/
- IBM WebSphere 9060, 9043, 9080 → https://www.ibm.com/docs/en/was/9.0.5?topic=servers-port-number-settings
- WildFly 9990 → https://docs.wildfly.org/31/Admin_Guide.html
- GlassFish 4848 → https://glassfish.org/docs/latest/administration-guide.html
- Apache Solr 8983 → https://solr.apache.org/guide/solr/latest/deployment-guide/taking-solr-to-production.html
- Jupyter 8888 → https://jupyter-server.readthedocs.io/en/latest/other/full-config.html

## Messaging
- Apache Kafka 9092 → https://kafka.apache.org/documentation/#brokerconfigs
- Apache ZooKeeper 2181 → https://zookeeper.apache.org/doc/current/zookeeperStarted.html
- RabbitMQ 5672, 5671, 15672, 4369, 25672, 1883, 8883 → https://www.rabbitmq.com/docs/networking#ports
- Apache ActiveMQ 61616, 8161 → https://activemq.apache.org/components/classic/documentation/
- NATS 4222, 6222, 8222 → https://docs.nats.io/running-a-nats-service/configuration

## DevOps
- Kubernetes 6443, 2379-2380, 10250, 10256, 10257, 10259, 30000-32767 [checked] → https://kubernetes.io/docs/reference/networking/ports-and-protocols/
- Docker Engine 2375/2376 → https://docs.docker.com/engine/daemon/remote-access/
- Docker Swarm 2377, 7946, udp:4789 → https://docs.docker.com/engine/swarm/swarm-tutorial/#open-protocols-and-ports-between-the-hosts
- Docker Registry 5000 → https://distribution.github.io/distribution/about/deploying/
- Portainer 9443, 9000, 8000 → https://docs.portainer.io/start/requirements-and-prerequisites
- Jenkins 8080, 50000 → https://www.jenkins.io/doc/book/installing/docker/
- TeamCity 8111 → https://www.jetbrains.com/help/teamcity/configuring-server-url.html
- Bamboo 8085 → https://confluence.atlassian.com/bamboo/bamboo-ports-reference-1489801047.html
- Bitbucket Data Center 7990, 7999 → https://confluence.atlassian.com/bitbucketserver/ports-used-by-bitbucket-data-center-776640295.html
- Gitea 3000 → https://docs.gitea.com/administration/config-cheat-sheet
- Sonatype Nexus 8081 → https://help.sonatype.com/en/configuring-the-runtime-environment.html
- JFrog Artifactory 8081, 8082 → https://jfrog.com/help/r/jfrog-installation-setup-documentation/system-requirements
- SonarQube 9000 → https://docs.sonarsource.com/sonarqube-server/latest/setup-and-upgrade/install-the-server/
- Puppet 8140 → https://www.puppet.com/docs/puppet/8/server/install_from_packages
- Salt 4505/4506 → https://docs.saltproject.io/en/latest/topics/tutorials/firewall.html
- HashiCorp Vault 8200, 8201 → https://developer.hashicorp.com/vault/docs/configuration/listener/tcp
- HashiCorp Consul 8500, 8300, 8301-8302 → https://developer.hashicorp.com/consul/docs/install/ports
- HashiCorp Nomad 4646-4648 → https://developer.hashicorp.com/nomad/docs/install/production/requirements#ports-used
- Apache Hadoop 9870, 8020, 8088 → https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-hdfs/hdfs-default.xml
- Apache Spark 7077 → https://spark.apache.org/docs/latest/security.html#configuring-ports-for-network-security

## Monitoring and logging
- Zabbix 10050, 10051 → https://www.zabbix.com/documentation/current/en/manual/installation/requirements
- Nagios NRPE 5666, NSCA 5667, NCPA 5693 → https://assets.nagios.com/downloads/nagiosxi/docs/Nagios-XI-Network-Ports.pdf
- Paessler PRTG 23560 → https://www.paessler.com/manuals/prtg/prtg_ports
- Checkmk 6556, 8000 → https://docs.checkmk.com/latest/en/ports.html
- Icinga 2 5665 → https://icinga.com/docs/icinga-2/latest/doc/06-distributed-monitoring/
- SolarWinds Orion agent 17778 → https://documentation.solarwinds.com/en/success_center/orionplatform/content/system_requirements/port_requirements_for_all_solarwinds_products.htm
- Grafana 3000 → https://grafana.com/docs/grafana/latest/setup-grafana/configure-grafana/
- Prometheus 9090, 9093, 9100 → https://github.com/prometheus/prometheus/wiki/Default-port-allocations
- Netdata 19999 → https://learn.netdata.cloud/docs/netdata-agent/configuration/
- Datadog DogStatsD udp:8125 → https://docs.datadoghq.com/developers/dogstatsd/
- Kibana 5601, Logstash 5044/9600, Fleet 8220 → https://www.elastic.co/guide/en/fleet/current/add-fleet-server-on-prem.html and https://www.elastic.co/guide/en/logstash/current/monitoring-logstash.html
- Graylog 9000, 12201 → https://go2docs.graylog.org/current/setting_up_graylog/default_file_locations.html
- Splunk 8000, 8089, 9997, 8088 → https://docs.splunk.com/Documentation/Splunk/latest/InheritedDeployment/Ports
- Wazuh 1514, 1515, 55000 → https://documentation.wazuh.com/current/getting-started/architecture.html
- HP JetDirect 9100 → https://support.hp.com/us-en/document/ish_3943009-3943072-16

## Security tools
- Tenable Nessus 8834 → https://docs.tenable.com/nessus/Content/NessusPortRequirements.htm
- Rapid7 InsightVM 3780 → https://docs.rapid7.com/insightvm/console-installation/
- Greenbone GSA 9392 → https://greenbone.github.io/docs/latest/22.4/source-build/index.html
- Kaspersky Security Center 13000, 14000, 13291 → https://support.kaspersky.com/KSC/14.2/en-US/158830.htm
- ESET PROTECT 2222, 2223 → https://help.eset.com/protect_admin/latest/en-US/ports_used.html
- Trellix ePO 8443, 8444, 8081 → https://docs.trellix.com/bundle/epolicy-orchestrator-on-prem-5.10.0-installation-guide/page/GUID-6DBE9C15-8F6B-4C6A-A4EC-47FFF7F2A35B.html
- Symantec SEPM 8443, 8014 → https://knowledge.broadcom.com/external/article/151340
- CyberArk Vault 1858 → https://docs.cyberark.com/pam-self-hosted/latest/en/content/pas%20inst/network-port-communication.htm
- RSA Authentication Manager 5500, 7004 → https://community.rsa.com/s/article/Port-Usage
- Velociraptor 8000, 8889 → https://docs.velociraptor.app/docs/deployment/

## Remote access tools
- TeamViewer 5938 → https://www.teamviewer.com/en/global/support/knowledge-base/teamviewer-classic/troubleshooting/which-ports-are-used-by-teamviewer/
- AnyDesk 7070 → https://support.anydesk.com/knowledge/firewall
- RustDesk 21115-21119 → https://rustdesk.com/docs/en/self-host/rustdesk-server-oss/install/
- ConnectWise ScreenConnect 8040, 8041 → https://docs.connectwise.com/ScreenConnect_Documentation/On-premises/Advanced_setup/Port_configuration
- NoMachine 4000 → https://kb.nomachine.com/AR04S01122
- Apache Guacamole 4822 → https://guacamole.apache.org/doc/gug/configuring-guacamole.html
