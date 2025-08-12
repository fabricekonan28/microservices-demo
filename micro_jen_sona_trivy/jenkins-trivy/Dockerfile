FROM jenkins/jenkins:lts

USER root

# 1. Installer les dépendances nécessaires
RUN apt-get update && \
    apt-get install -y wget apt-transport-https gnupg software-properties-common && \
    rm -rf /var/lib/apt/lists/*

# 2. Ajouter le dépôt Trivy correctement (méthode officielle)
RUN wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | apt-key add - && \
    echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | tee -a /etc/apt/sources.list.d/trivy.list

# 3. Installer Trivy
RUN apt-get update && \
    apt-get install -y trivy && \
    trivy --version && \
    rm -rf /var/lib/apt/lists/*

USER jenkins