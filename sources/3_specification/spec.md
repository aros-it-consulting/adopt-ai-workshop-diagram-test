# Spécification fonctionnelle — Retours et remboursements

Orvane, direction de l'expérience client\
Référence : SF-RET\
Version en vigueur : 2.3 du 12 janvier 2026\
Diffusion interne : service client, entrepôt, comptabilité, équipe marketplace, équipe produit

## 1. Objet et périmètre

### 1.1 Objet

Orvane vend sur son site des articles pour la maison et le jardin. Une partie du catalogue vient de son propre stock : c'est la vente directe. L'autre partie est proposée par des vendeurs partenaires, réunis sur sa marketplace.

Ce document décrit ce qu'il advient d'un article qu'un client renvoie : les conditions auxquelles Orvane ou le vendeur le reprend, le chemin que suit le colis, le calcul du montant remboursé et le délai dans lequel le client est remboursé.

Le service client, l'entrepôt et la comptabilité s'y réfèrent pour traiter un retour. L'équipe produit, chargée de l'espace client et de l'outil de gestion des retours, en part pour faire évoluer ces deux outils. Les conditions générales de vente publiées sur le site reprennent les engagements qu'Orvane y prend envers ses clients.

### 1.2 Périmètre

La spécification couvre les retours d'articles livrés en France métropolitaine, pour les clients particuliers et les clients professionnels, en vente directe et en marketplace.

Quatre sujets voisins sont traités ailleurs :

- l'annulation d'une commande avant son expédition, décrite dans la spécification des commandes ;
- l'échange d'un article, qu'Orvane ne propose pas : le client retourne l'article, puis passe une nouvelle commande ;
- la panne qui survient après le délai de retour, que le service après-vente prend en charge au titre de la garantie ;
- les commandes livrées hors de France métropolitaine, dont le service client règle les retours au cas par cas.

### 1.3 Versions et avenants

| Version | Date | Objet de la révision |
| ------- | ---------- | ------------------------------------------------ |
| 1.0 | 4 mars 2024 | Première version : retours en vente directe |
| 2.0 | 16 juin 2025 | Ouverture de la marketplace : vendeurs partenaires, canal de vente, statut RECU_VENDEUR |
| 2.1 | 15 septembre 2025 | Paiement en plusieurs fois (RG-10) |
| 2.2 | 3 novembre 2025 | Retours de fin d'année (RG-01), remboursement sans retour (RG-24) |
| 2.3 | 12 janvier 2026 | Grille de décote (annexe C), contestation des refus (RG-21) |

Entre deux versions, une modification qui ne peut pas attendre fait l'objet d'un avenant numéroté et daté, placé à la fin du document. Le corps du texte et les tableaux ne sont pas réécrits pour autant. Seule la colonne « Statut » du tableau des règles (section 5.2) change : elle signale la règle modifiée ou abrogée et renvoie à l'avenant, qui en donne la rédaction applicable. Lorsque le corps du document et un avenant se contredisent, l'avenant l'emporte. La version suivante reprend le contenu des avenants dans le texte, puis les supprime.

## 2. Définitions

| Terme | Définition |
| ---------------- | ------------------------------------------------------------ |
| Vente directe | Vente d'un article du stock d'Orvane, facturée par Orvane. |
| Marketplace | Partie du site où des vendeurs partenaires proposent leurs propres articles. Le vendeur facture le client ; Orvane encaisse le paiement pour son compte et lui reverse le prix, commission déduite. |
| Canal | Vente directe ou marketplace. Le canal d'une ligne de commande est celui du vendeur de l'article, quel que soit l'entrepôt qui l'expédie[^1]. |
| Vendeur partenaire | Entreprise tierce qui vend sur la marketplace, sous contrat avec Orvane. |
| Client particulier | Personne qui achète pour ses besoins personnels. |
| Client professionnel | Entreprise, artisan, collectivité ou association titulaire d'un compte professionnel, ouvert sur présentation d'un numéro SIRET. |
| Retour | Renvoi par le client d'un ou de plusieurs articles d'une même commande. Un retour porte un numéro, un statut (annexe A) et une ligne par article renvoyé. |
| Retour de convenance | Retour d'un article conforme, que le client ne souhaite pas garder. |
| Non-conformité | État d'un article défectueux, abîmé pendant le transport, incomplet ou différent de l'article commandé. |
| Article volumineux | Article de plus de 30 kg, ou dont une dimension dépasse 150 cm, livré par un transporteur spécialisé. |
| Contrôle | Examen des articles reçus, ligne par ligne, par l'entrepôt d'Orvane ou par le vendeur partenaire. |
| Décote | Réduction du montant remboursé pour un article repris en moins bon état qu'à la livraison (annexe C). |
| Avoir | Pièce comptable qui annule tout ou partie d'une facture. Chaque remboursement s'appuie sur un avoir. |
| Carte cadeau | Carte prépayée émise par Orvane, en plastique ou dématérialisée, utilisable sur les deux canaux jusqu'à épuisement de son solde. |
| Délai de remboursement | Nombre de jours calendaires entre le point de départ fixé par RG-03 et l'émission du remboursement par Orvane. Le temps que met ensuite la banque du client à créditer son compte n'en fait pas partie. |
| Jour ouvré | Jour du lundi au vendredi, hors jours fériés. |

[^1]: Certains vendeurs partenaires confient leur stock à l'entrepôt d'Orvane. Leurs articles relèvent du canal marketplace, bien qu'Orvane les expédie et en reçoive les retours.

## 3. Acteurs

| Acteur | Rôle dans un retour |
| ---------------- | ------------------------------------------------------------ |
| Client | Dépose la demande, emballe le colis et le remet au transporteur, reçoit le remboursement. Peut contester un refus. |
| Service client | Répond au client, tranche les cas que les règles ne prévoient pas, valide les demandes pour non-conformité, instruit les contestations. |
| Entrepôt d'Orvane | Reçoit et contrôle les retours de vente directe et ceux des vendeurs dont il loge le stock. Remet les articles en stock, les déclasse ou les recycle. |
| Vendeur partenaire | Reçoit et contrôle les retours des articles qu'il expédie lui-même. Saisit sa décision dans l'outil de gestion des retours. |
| Transporteur | Achemine le colis retourné. Un transporteur spécialisé enlève les articles volumineux chez le client. |
| Comptabilité | Émet l'avoir, ordonne le remboursement, reprend au vendeur partenaire les sommes reversées. |
| Prestataire de paiement | Exécute les remboursements par carte bancaire et annule les échéances d'un paiement en plusieurs fois. |
| Outil de gestion des retours | Porte le statut de chaque retour, applique les règles automatiques (recevabilité, délais, notifications) et garde la trace de chaque décision. |

En marketplace, le client n'a qu'un interlocuteur, Orvane. Il dépose sa demande dans le même espace client, reçoit les mêmes notifications, et c'est Orvane qui le rembourse. Le vendeur partenaire intervient à deux moments : lorsqu'il contrôle les articles qu'il reçoit, puis lorsqu'Orvane lui reprend les sommes remboursées.

Un conseiller du service client peut toujours revenir sur une décision automatique, forcer un statut ou accorder un geste commercial. Il saisit alors un motif, que l'outil conserve avec son nom et la date.

## 4. Parcours d'un retour

Un retour va de la demande du client à son remboursement en six étapes, auxquelles s'ajoute la contestation lorsque le client n'accepte pas la décision. L'annexe A donne la liste des statuts qu'il prend en chemin, et l'annexe B les passages autorisés de l'un à l'autre.

### 4.1 Demande de retour

Le client ouvre sa demande depuis son espace client, à partir de la commande concernée. Il choisit les articles à renvoyer, leur quantité et, pour chacun, un motif de la liste de l'annexe D. Pour un motif de non-conformité, il joint au moins une photographie. L'outil crée un retour au statut DEMANDE_RECUE, avec une ligne par article.

Un retour ne part que vers une seule adresse. Une commande qui mêle des articles de vente directe et des articles de plusieurs vendeurs donne donc lieu à autant de retours qu'il y a de vendeurs concernés, Orvane compris.

Tant qu'il n'a pas remis son colis au transporteur, le client peut renoncer à son retour depuis son espace client. Le retour passe alors au statut ANNULE.

### 4.2 Recevabilité

L'outil vérifie aussitôt le délai de retour (RG-01 pour un client particulier, RG-02 pour un client professionnel) et la présence d'articles non repris. Une demande hors délai, ou qui ne porte que sur des articles non repris, passe au statut DEMANDE_IRRECEVABLE. Le client en est informé, avec le motif.

Lorsque le motif déclaré est une non-conformité, la demande suit RG-17. Un conseiller du service client la valide au vu des photographies, dans les deux jours ouvrés.

### 4.3 Expédition par le client

Pour une demande recevable, l'outil émet une étiquette de retour prépayée. S'il s'agit d'un article volumineux, il propose un rendez-vous d'enlèvement[^2]. Le retour passe au statut ETIQUETTE_EMISE. Le client a alors 14 jours pour remettre son colis au transporteur (RG-19). Dès que le suivi du transporteur indique la prise en charge du colis, le retour passe au statut EN_TRANSIT.

[^2]: Le transporteur propose un créneau dans les 5 jours ouvrés. Après deux rendez-vous manqués par le client, le retour passe au statut EXPIRE.

### 4.4 Réception et contrôle

Le colis arrive à l'entrepôt d'Orvane (statut RECU_ENTREPOT) ou chez le vendeur partenaire (statut RECU_VENDEUR). Le contrôle commence à l'ouverture du colis, et le retour passe au statut EN_CONTROLE. RG-23 fixe le temps laissé à l'entrepôt et au vendeur pour le mener.

Le contrôleur examine chaque ligne du retour. Il vérifie que l'article est bien celui de la commande, qu'il est complet, avec ses accessoires et sa notice, et qu'il peut être remis en vente. Pour une non-conformité, il confirme ou écarte le défaut déclaré par le client. Il saisit ensuite son résultat dans l'outil, ligne par ligne : article repris, article repris avec une décote (annexe C) ou article refusé. Un refus ou une décote s'accompagne d'un motif et d'une photographie.

Lorsque le contrôle ne retrouve pas le défaut déclaré, le retour redevient un retour de convenance : les frais de retour sont dus (RG-18) et un article exclu du retour de convenance est refusé.

### 4.5 Décision

Le contrôle se conclut par l'un de ces trois statuts :

- ACCEPTE, lorsque tous les articles sont repris sans décote ;
- REFUSE, lorsqu'aucun article n'est repris ;
- REFUSE_PARTIEL, lorsqu'une partie seulement des articles est reprise (RG-14) ou qu'une décote s'applique à l'un d'eux au moins (RG-16).

Le client reçoit la décision par courriel (RG-20). Les articles repris rejoignent le stock, le second choix ou le recyclage, selon leur état. Ce tri n'a aucun effet sur le remboursement.

### 4.6 Remboursement

La comptabilité émet l'avoir (section 6.6), puis ordonne le remboursement vers le moyen de paiement de la commande. Le montant part du prix payé pour les articles repris (RG-11). La comptabilité y ajoute les frais de livraison de la commande lorsqu'ils sont dus (RG-13) et en retranche la décote (RG-16) et les frais de retour (RG-18).

Le délai dépend du canal, du moyen de paiement et du type de client (section 5.3) ; voir RG-03 pour son point de départ. L'émission du remboursement fait passer le retour au statut REMBOURSE.

### 4.7 Contestation

Le client qui n'accepte pas un refus ou une décote le conteste depuis son espace client. Il explique son désaccord et joint les pièces qu'il juge utiles (RG-21). Le retour passe au statut LITIGE. Un conseiller du service client reprend le dossier, consulte les photographies du contrôle et peut demander un second contrôle à l'entrepôt ou au vendeur partenaire. Sa décision confirme le résultat du contrôle ou le révise, en tout ou en partie.

La contestation ne suspend pas le remboursement des articles déjà repris.

## 5. Règles de gestion

### 5.1 Lecture des règles

Chaque règle porte un identifiant, de RG-01 à RG-24, que l'outil de gestion des retours et les autres documents d'Orvane reprennent tel quel. Un identifiant n'est jamais réattribué, et une règle abrogée garde le sien.

La colonne « Statut » dit si la règle s'applique telle qu'elle est écrite. Elle prend trois valeurs :

- « En vigueur » : la règle s'applique dans la rédaction du tableau ;
- « Modifiée par l'avenant n° … » : la règle s'applique dans la rédaction de l'avenant cité, qui remplace celle du tableau ;
- « Abrogée par l'avenant n° … » : la règle ne s'applique plus.

Sauf mention contraire, les délais se comptent en jours calendaires et les montants s'entendent toutes taxes comprises.

### 5.2 Tableau des règles

| Identifiant | Règle | Statut |
| ------------ | ---------------------------------------------------------- | -------------- |
| RG-01 | Un client particulier peut retourner un article dans les 30 jours qui suivent sa livraison, sans avoir à donner de raison, en vente directe comme en marketplace[^3]. Certains articles ne sont pas repris[^4]. | En vigueur |
| RG-02 | Un client professionnel peut retourner un article dans les 14 jours qui suivent sa livraison, à condition que l'article soit dans son emballage d'origine, non ouvert. Les exclusions de RG-01 s'appliquent, ainsi que celle des commandes sur devis[^5]. | En vigueur |
| RG-03 | Le délai de remboursement court à compter du passage du retour au statut ACCEPTE[^6]. Orvane rembourse sur le moyen de paiement utilisé à la commande, selon RG-04 à RG-10, et sur aucun autre, même à la demande du client. | En vigueur |
| RG-04 | Vente directe, paiement par carte bancaire : Orvane rembourse sur la carte utilisée dans un délai de 3 jours, pour un client particulier comme pour un client professionnel. | En vigueur |
| RG-05 | Vente directe, paiement par virement : Orvane rembourse par virement vers le compte d'origine[^7] dans un délai de 5 jours pour un client particulier et de 10 jours pour un client professionnel, sous réserve de RG-15. | En vigueur |
| RG-06 | Paiement par carte cadeau : Orvane recrédite la carte cadeau utilisée[^8] dans un délai de 2 jours en vente directe, pour tous les clients, et de 5 jours en marketplace pour un client particulier. | En vigueur |
| RG-07 | Marketplace, paiement par carte cadeau, client professionnel : Orvane recrédite la carte cadeau dans un délai de 30 jours, après le rapprochement mensuel des ventes et des retours avec le vendeur partenaire. | Modifiée par l'avenant n° 1 |
| RG-08 | Marketplace, paiement par carte bancaire : Orvane rembourse sur la carte utilisée dans un délai de 7 jours pour un client particulier et de 14 jours pour un client professionnel. | En vigueur |
| RG-09 | Marketplace, paiement par virement : Orvane rembourse par virement dans un délai de 10 jours pour un client particulier et de 21 jours pour un client professionnel, sous réserve de RG-15. Les conditions de RG-05 sur le compte d'origine s'appliquent. | En vigueur |
| RG-10 | Paiement en plusieurs fois, réservé aux clients particuliers : Orvane rembourse les échéances déjà prélevées dans un délai de 7 jours en vente directe et de 10 jours en marketplace, et fait annuler les échéances à venir[^9]. | En vigueur |
| RG-11 | Orvane rembourse le prix que le client a payé pour chaque article repris, remises et codes promotionnels déduits, sous réserve de RG-12 et de RG-16. Les frais de retour sont retenus selon RG-18. | En vigueur |
| RG-12 | Retour de convenance d'un client professionnel en vente directe : Orvane retient sur le remboursement des frais de remise en stock, égaux à 10 % du prix hors taxes des articles repris. | Abrogée par l'avenant n° 1 |
| RG-13 | Orvane rembourse les frais de livraison de la commande, au tarif de la livraison standard, lorsque le client retourne tous les articles de cette commande. Lorsqu'il en garde une partie, ces frais ne sont pas remboursés. Pour une non-conformité, voir RG-17. | En vigueur |
| RG-14 | Lorsque le contrôle ne reprend qu'une partie des articles d'un retour, le retour passe au statut REFUSE_PARTIEL. Orvane ne rembourse que les articles repris. | En vigueur |
| RG-15 | Client professionnel qui règle par virement à échéance : tant qu'il n'a pas payé la facture de la commande, Orvane ne lui verse aucun remboursement. L'avoir vient en déduction de la facture, et le délai de remboursement est sans objet. | En vigueur |
| RG-16 | Un article repris incomplet, sali, utilisé ou abîmé par le client subit une décote de 10 % à 50 % de son prix, selon la grille de l'annexe C. Le retour passe alors au statut REFUSE_PARTIEL. Un article dont l'état appellerait une décote supérieure est refusé. | En vigueur |
| RG-17 | Une non-conformité se déclare dans les 30 jours qui suivent la livraison, pour tous les clients et tous les articles, y compris ceux que RG-01 et RG-02 excluent. Orvane, ou le vendeur partenaire en marketplace, supporte les frais de retour. Orvane rembourse le prix de l'article et les frais de livraison de la commande. | En vigueur |
| RG-18 | Les frais d'un retour de convenance sont à la charge du client. Orvane retient sur le remboursement 6,90 € par colis pour une étiquette prépayée et 39 € par enlèvement pour un article volumineux[^10]. | En vigueur |
| RG-19 | Le client remet son colis au transporteur dans les 14 jours qui suivent le statut ETIQUETTE_EMISE. Passé ce délai, le retour passe au statut EXPIRE. Le client peut déposer une nouvelle demande si le délai de RG-01 ou de RG-02 court encore. | En vigueur |
| RG-20 | L'outil de gestion des retours informe le client par courriel à chaque changement de statut. Pour les statuts REFUSE et REFUSE_PARTIEL, la notification donne le motif du refus ou de la décote, article par article, et le montant qui sera remboursé. | En vigueur |
| RG-21 | Le client a 15 jours, à compter de la notification, pour contester un refus ou une décote. Le service client rend sa décision dans les 10 jours qui suivent la contestation. Cette décision est définitive. | En vigueur |
| RG-22 | Orvane, ou le vendeur partenaire, garde les articles refusés pendant 30 jours à compter de la notification. Le client peut demander qu'ils lui soient réexpédiés, à ses frais. Passé ce délai, les articles sont donnés à une association ou recyclés. | En vigueur |
| RG-23 | Le contrôle a lieu dans les 2 jours ouvrés qui suivent le statut RECU_ENTREPOT, et dans les 5 jours ouvrés qui suivent le statut RECU_VENDEUR. Si le vendeur partenaire n'a pas rendu sa décision dans ce délai, le retour passe d'office au statut ACCEPTE. | En vigueur |
| RG-24 | Pour un article non conforme dont le prix est inférieur à 20 €, le service client peut rembourser le client sans lui demander de renvoyer l'article[^11]. Le retour passe directement au statut REMBOURSE_SANS_RETOUR. | En vigueur |

[^3]: Un article livré entre le 1er novembre et le 24 décembre peut être retourné jusqu'au 31 janvier suivant.

[^4]: Ne sont pas repris en retour de convenance : les végétaux, les articles fabriqués sur mesure ou personnalisés, les produits phytosanitaires et les peintures dont l'emballage a été ouvert, la literie sortie de son film de protection. La non-conformité de ces articles reste couverte (voir RG-17).

[^5]: Une commande passée sur devis, dont le service commercial a négocié les quantités ou les prix, n'ouvre droit à aucun retour de convenance. Seule la non-conformité est recevable (RG-17).

[^6]: Pour un retour au statut REFUSE_PARTIEL, le délai court à compter de l'envoi au client de la notification de la décision.

[^7]: Lorsque le compte d'origine est clos ou que la banque rejette le virement, le service client demande au client un relevé d'identité bancaire à son nom. Le délai repart de la réception de ce relevé.

[^8]: Si la carte cadeau a expiré depuis la commande, Orvane en émet une nouvelle, du montant remboursé et valable douze mois.

[^9]: Lorsque le remboursement ne couvre qu'une partie de la commande, notamment pour un retour au statut REFUSE_PARTIEL, son montant s'impute d'abord sur les échéances à venir, en commençant par la dernière. Orvane ne reverse sur la carte bancaire que ce qui dépasse le total de ces échéances.

[^10]: Un retour au statut REFUSE_PARTIEL supporte ces frais en totalité, quel que soit le nombre d'articles refusés.

[^11]: Dans la limite de trois remboursements sans retour par client sur douze mois glissants. Au-delà, le service client exige le renvoi de l'article.

### 5.3 Délais de remboursement par canal, moyen de paiement et type de client

Les règles RG-04 à RG-10 fixent un délai pour chaque combinaison de canal, de moyen de paiement et de type de client. Le délai se compte en jours calendaires depuis le point de départ de RG-03. Le paiement en plusieurs fois n'est pas proposé aux clients professionnels et n'a donc qu'une ligne par canal.

Chaque ligne renvoie à la règle qui la fonde, dont le statut se lit dans le tableau de la section 5.2.

| Canal | Moyen de paiement | Type de client | Délai de remboursement | Règle |
| ------------- | -------------------------- | ------------- | ------------ | --------- |
| Vente directe | Carte bancaire | Particulier | 3 jours | RG-04 |
| Vente directe | Carte bancaire | Professionnel | 3 jours | RG-04 |
| Vente directe | Virement | Particulier | 5 jours | RG-05 |
| Vente directe | Virement | Professionnel | 10 jours | RG-05 |
| Vente directe | Carte cadeau | Particulier | 2 jours | RG-06 |
| Vente directe | Carte cadeau | Professionnel | 2 jours | RG-06 |
| Vente directe | Paiement en plusieurs fois | Particulier | 7 jours | RG-10 |
| Marketplace | Carte bancaire | Particulier | 7 jours | RG-08 |
| Marketplace | Carte bancaire | Professionnel | 14 jours | RG-08 |
| Marketplace | Virement | Particulier | 10 jours | RG-09 |
| Marketplace | Virement | Professionnel | 21 jours | RG-09 |
| Marketplace | Carte cadeau | Particulier | 5 jours | RG-06 |
| Marketplace | Carte cadeau | Professionnel | 30 jours | RG-07 |
| Marketplace | Paiement en plusieurs fois | Particulier | 10 jours | RG-10 |

Une commande réglée par plusieurs moyens de paiement suit, pour chaque part, le délai du moyen concerné (section 6.5).

## 6. Modalités de remboursement

### 6.1 Carte bancaire

Le prestataire de paiement recrédite la carte qui a servi à la commande, sur ordre de la comptabilité. Orvane ne conserve aucun numéro de carte : l'ordre de remboursement désigne la transaction d'origine, que le prestataire retrouve. Lorsque la carte a expiré ou a été renouvelée entre-temps, la banque du client reporte d'elle-même la somme sur le compte auquel la carte était rattachée.

Le remboursement apparaît sur le relevé du client sous le libellé « ORVANE REMB », suivi du numéro du retour. Selon les banques, il y figure deux à cinq jours après son émission. Ce temps bancaire s'ajoute au délai de remboursement.

### 6.2 Virement

Le virement sert surtout aux clients professionnels. Les clients particuliers y recourent pour les commandes dont le montant dépasse le plafond de leur carte. Orvane rembourse par virement vers le compte qui a émis le paiement, dont les coordonnées figurent sur son relevé bancaire (RG-05, RG-09).

Un client professionnel peut avoir obtenu du service commercial de régler à échéance, à 30 jours fin de mois. Si son retour est accepté avant qu'il ait payé sa facture, Orvane n'a rien à lui rembourser : l'avoir réduit d'autant la somme qu'il doit (RG-15). Si la facture est déjà payée, RG-05 ou RG-09 s'applique.

### 6.3 Carte cadeau

Une commande réglée par carte cadeau se rembourse sur la carte cadeau. Orvane la recrédite du montant remboursé, que le client peut dépenser sur les deux canaux. Le solde d'une carte cadeau ne se convertit ni en virement ni en remboursement sur carte bancaire.

En vente directe, la somme n'a pas quitté les comptes d'Orvane et le recrédit suit de près l'acceptation du retour. En marketplace, Orvane a déjà reversé le prix au vendeur partenaire. Pour un client particulier, Orvane recrédite la carte sans attendre d'avoir repris cette somme au vendeur (RG-06). Les clients professionnels achètent le plus souvent leurs cartes cadeaux en nombre et sur facture : pour eux, le recrédit attend le rapprochement des ventes et des retours avec le vendeur, et une règle distincte en fixe le délai (section 5.3).

### 6.4 Paiement en plusieurs fois

Les clients particuliers peuvent régler en trois ou quatre échéances mensuelles, par carte bancaire, une commande de 150 € à 3 000 €. Le prestataire de paiement prélève la première échéance à la commande. Lorsqu'un retour est accepté, la comptabilité lui transmet le montant à rembourser. Le prestataire annule ou réduit les échéances à venir et, s'il reste une somme due au client, recrédite sa carte (RG-10).

Le prestataire facture des frais pour un paiement en quatre fois. Orvane les rembourse avec la commande lorsque le client la retourne en entier.

### 6.5 Commande réglée par plusieurs moyens de paiement

Un client peut compléter une carte cadeau par une carte bancaire. Le remboursement se répartit alors entre les deux moyens de paiement, à proportion de ce que chacun a réglé, et chaque part suit le délai de son moyen de paiement.

Ainsi, pour une commande de 200 € payée 50 € par carte cadeau et 150 € par carte bancaire, le retour d'un article de 80 € donne lieu à un recrédit de 20 € sur la carte cadeau et à un remboursement de 60 € sur la carte bancaire.

### 6.6 Avoir et écritures comptables

La comptabilité émet un avoir avant d'ordonner chaque remboursement. L'avoir reprend les lignes concernées de la facture, la décote appliquée et les frais de retour retenus. En vente directe, Orvane l'émet en son nom. En marketplace, Orvane l'émet au nom et pour le compte du vendeur partenaire, comme la facture d'origine.

Orvane reprend ensuite au vendeur le montant net qui lui avait été reversé pour les articles repris, et renonce à sa commission sur ces articles. Ces écritures passent par le rapprochement périodique entre Orvane et chaque vendeur. Elles ne changent rien au délai dans lequel le client est remboursé, sauf dans le cas que décrit la section 6.3.

## 7. Cas particuliers

### 7.1 Articles volumineux

Un article volumineux ne voyage pas par colis : le transporteur spécialisé vient le chercher chez le client, sur rendez-vous. Le client le remet démonté et emballé comme il l'a reçu ou, à défaut, protégé de façon à supporter le transport. Le chauffeur ne contrôle pas l'article. Il note le nombre de colis enlevés sur un bon que signe le client.

Les frais d'enlèvement de RG-18 s'appliquent aux retours de convenance. Pour une non-conformité, RG-17 les met à la charge d'Orvane ou du vendeur partenaire.

### 7.2 Colis perdu pendant le retour

Tant que le client utilise l'étiquette fournie, le colis voyage aux risques d'Orvane. Si le suivi ne montre plus aucun mouvement pendant 10 jours après le statut EN_TRANSIT, le service client ouvre une enquête auprès du transporteur. Sans nouvelles 10 jours plus tard, le colis est tenu pour perdu : le service client passe le retour au statut ACCEPTE, et le remboursement suit son cours.

Le client qui préfère un transporteur de son choix expédie à ses risques et à ses frais. Orvane ne le rembourse qu'après avoir reçu et contrôlé le colis.

### 7.3 Colis reçu sans demande préalable

Il arrive qu'un colis parvienne à l'entrepôt sans numéro de retour, parce que le client a renvoyé l'article de sa propre initiative. L'entrepôt le met de côté et le signale au service client, qui recherche la commande à partir du nom de l'expéditeur et de l'article reçu. Une fois le client identifié, le conseiller crée le retour directement au statut RECU_ENTREPOT. La recevabilité s'apprécie alors à la date de réception du colis.

Un colis dont l'expéditeur reste inconnu après 60 jours suit le sort des articles refusés que leur propriétaire n'a pas réclamés (RG-22).

### 7.4 Lots et articles offerts

Un lot vendu sous une seule référence, par exemple un salon de jardin de cinq pièces, se retourne entier. Si une pièce manque à la réception, l'entrepôt applique la décote de l'annexe C ou refuse le lot.

Lorsqu'une promotion a offert un article pour l'achat d'un autre, le client qui retourne l'article payé renvoie aussi l'article offert. S'il le garde, Orvane retient son prix catalogue sur le remboursement.

### 7.5 Vendeur partenaire défaillant

Lorsqu'un vendeur partenaire cesse de répondre, ou que son contrat prend fin alors que des retours sont en cours, Orvane prend sa place. Les retours qui ne sont pas encore expédiés sont dirigés vers l'entrepôt d'Orvane, qui les contrôle. Le client est remboursé dans les délais de la marketplace. Orvane réclame ensuite les sommes au vendeur, comme le prévoit son contrat.

## Annexe A. Codes de statut d'un retour

Un retour n'a qu'un statut à la fois. L'outil de gestion des retours, l'espace client et les exports comptables emploient les mêmes codes.

| Code | Signification | Règles |
| -------------------- | ------------------------------------------------------ | ---------------- |
| DEMANDE_RECUE | La demande est enregistrée. L'outil n'a pas encore vérifié sa recevabilité. | RG-01, RG-02 |
| DEMANDE_IRRECEVABLE | La demande est hors délai, ou ne porte que sur des articles non repris. Statut final. | RG-01, RG-02 |
| ETIQUETTE_EMISE | La demande est recevable. Le client a reçu son étiquette ou son rendez-vous d'enlèvement. | RG-18, RG-19 |
| EN_TRANSIT | Le transporteur a pris le colis en charge. | RG-19 |
| RECU_ENTREPOT | Le colis est arrivé à l'entrepôt d'Orvane. | RG-23 |
| RECU_VENDEUR | Le colis est arrivé chez le vendeur partenaire. | RG-23 |
| EN_CONTROLE | Le colis est ouvert, le contrôle des articles est en cours. | RG-23 |
| ACCEPTE | Tous les articles du retour sont repris, sans décote. | RG-03, RG-23 |
| REFUSE | Aucun article n'est repris. | RG-20, RG-21, RG-22 |
| REFUSE_PARTIEL | Une partie seulement des articles est reprise, ou une décote s'applique à l'un d'eux au moins. | RG-14, RG-16, RG-20, RG-21, RG-22 |
| LITIGE | Le client conteste la décision. Le service client instruit sa contestation. | RG-21 |
| REMBOURSE | Orvane a émis le remboursement. Statut final, sauf contestation. | RG-03 |
| REMBOURSE_SANS_RETOUR | Orvane a remboursé le client sans lui demander de renvoyer l'article. Statut final. | RG-24 |
| EXPIRE | Le client n'a pas remis son colis à temps. Statut final. | RG-19 |
| ANNULE | Le client a renoncé à son retour avant de remettre le colis. Statut final. | Aucune |

## Annexe B. Passages d'un statut à l'autre

L'outil refuse tout passage absent de cette liste, sauf lorsqu'un conseiller du service client force un statut.

| Statut de départ | Statut d'arrivée | Déclencheur | Règle |
| ------------------------ | ------------------------ | -------------------------------------- | ---------- |
| DEMANDE_RECUE | DEMANDE_IRRECEVABLE | Vérification automatique : délai dépassé ou articles non repris | RG-01, RG-02 |
| DEMANDE_RECUE | ETIQUETTE_EMISE | Vérification automatique réussie, ou validation du service client pour une non-conformité | RG-17 |
| DEMANDE_RECUE | REMBOURSE_SANS_RETOUR | Décision du service client | RG-24 |
| ETIQUETTE_EMISE | EN_TRANSIT | Prise en charge du colis par le transporteur | RG-19 |
| ETIQUETTE_EMISE | EXPIRE | 14 jours sans prise en charge, ou deux rendez-vous d'enlèvement manqués | RG-19 |
| ETIQUETTE_EMISE | ANNULE | Renoncement du client | Aucune |
| EN_TRANSIT | RECU_ENTREPOT | Réception du colis à l'entrepôt d'Orvane | Aucune |
| EN_TRANSIT | RECU_VENDEUR | Réception du colis chez le vendeur partenaire | Aucune |
| EN_TRANSIT | ACCEPTE | Colis tenu pour perdu (section 7.2) | Aucune |
| RECU_ENTREPOT | EN_CONTROLE | Ouverture du colis | RG-23 |
| RECU_VENDEUR | EN_CONTROLE | Ouverture du colis | RG-23 |
| RECU_VENDEUR | ACCEPTE | 5 jours ouvrés sans décision du vendeur partenaire | RG-23 |
| EN_CONTROLE | ACCEPTE | Tous les articles repris, sans décote | RG-23 |
| EN_CONTROLE | REFUSE | Aucun article repris | RG-20 |
| EN_CONTROLE | REFUSE_PARTIEL | Une partie des articles refusée, ou une décote appliquée | RG-14, RG-16 |
| ACCEPTE | REMBOURSE | Émission du remboursement | RG-03 |
| REFUSE_PARTIEL | REMBOURSE | Émission du remboursement des articles repris | RG-03 |
| REFUSE | LITIGE | Contestation du client | RG-21 |
| REFUSE_PARTIEL | LITIGE | Contestation du client | RG-21 |
| REMBOURSE | LITIGE | Contestation d'un refus ou d'une décote après le remboursement des articles repris | RG-21 |
| LITIGE | ACCEPTE, REFUSE ou REFUSE_PARTIEL | Décision du service client | RG-21 |

## Annexe C. Grille de décote

La grille s'applique aux retours de convenance des clients particuliers. Un client professionnel dont l'article n'est plus dans son emballage d'origine, non ouvert, voit cet article refusé (RG-02).

| État constaté au contrôle | Décote |
| ------------------------------------------------------------ | ---------------- |
| Emballage d'origine absent ou détérioré, article intact | 10 % |
| Notice, visserie ou accessoire manquant | 20 % |
| Traces de montage ou d'utilisation, article propre et complet | 30 % |
| Article sali, rayé ou taché, revendable en second choix | 50 % |
| Article cassé, inutilisable, ou différent de l'article commandé | Refus de l'article |

Lorsque plusieurs états se cumulent, seule la décote la plus forte s'applique. La décote se calcule sur le prix payé pour l'article, remises déduites.

## Annexe D. Motifs de retour

Le client choisit un motif par article. La nature du motif décide des règles applicables : RG-01, RG-02 et RG-18 pour un retour de convenance, RG-17 pour une non-conformité.

| Code | Motif proposé au client | Nature |
| ----- | ---------------------------------------------------- | ---------------- |
| M01 | L'article ne me convient plus | Convenance |
| M02 | Les dimensions ne conviennent pas | Convenance |
| M03 | J'ai commandé par erreur, ou en double | Convenance |
| M04 | J'ai trouvé moins cher ailleurs | Convenance |
| M05 | L'article est arrivé abîmé | Non-conformité |
| M06 | L'article ne fonctionne pas | Non-conformité |
| M07 | Il manque une pièce ou un accessoire | Non-conformité |
| M08 | L'article reçu n'est pas celui que j'ai commandé | Non-conformité |
| M09 | L'article ne correspond pas à sa description | Non-conformité |

## Avenant n° 1

Avenant n° 1 à la version 2.3 du 12 janvier 2026\
Date d'effet : 4 mai 2026

### Motif

Le rapprochement des ventes et des retours avec les vendeurs partenaires, jusqu'ici mensuel, a lieu deux fois par mois depuis le 1er mai 2026. Le recrédit des cartes cadeaux des clients professionnels, qui attend ce rapprochement, peut donc intervenir plus tôt.

La direction commerciale a par ailleurs décidé de ne plus facturer de frais de remise en stock aux clients professionnels.

### Article 1. Modification de RG-07

RG-07 est remplacée par la rédaction suivante :

« Marketplace, paiement par carte cadeau, client professionnel : Orvane recrédite la carte cadeau dans un délai de 15 jours, après le rapprochement bimensuel des ventes et des retours avec le vendeur partenaire. »

Le délai de 30 jours qui figure dans le tableau des règles (section 5.2) et dans le tableau des délais (section 5.3) est donc ramené à 15 jours. Le point de départ fixé par RG-03 ne change pas.

### Article 2. Abrogation de RG-12

RG-12 est abrogée. Orvane ne retient plus de frais de remise en stock sur les retours de convenance des clients professionnels en vente directe.

RG-11 continue de s'appliquer. Sa réserve relative à RG-12 est sans objet.

### Article 3. Autres dispositions

Les autres règles et les annexes restent inchangées. La colonne « Statut » du tableau des règles signale les deux règles concernées. La version 3.0 reprendra le contenu de cet avenant.
