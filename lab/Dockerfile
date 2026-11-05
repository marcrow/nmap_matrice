# One image for every lab container: busybox nc for the services, nmap for the Sources,
# dnsmasq for the DNS server, iptables for the firewall.
FROM alpine:3.20
RUN apk add --no-cache nmap nmap-scripts dnsmasq iptables iproute2
