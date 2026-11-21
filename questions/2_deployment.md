Read the file sources/2_deployment/<file>, which describes the deployment of an online shop at a cloud provider.
Do not open any other file of the current folder or of its subfolders, whether to read it or to search it.
Answer the four questions from this file alone, as one JSON object whose keys are "1", "2", "3" and "4".
Write each name (a component, a VPC, a subnet, the label of a link) as the file writes it. A zone is "a", "b" or "c", and "none" for what sits in no zone.

1. The "Billing batch", in the "Application subnet" of "Zone b" of the "Paris region", calls a carrier's API on the "Internet". Which components does its traffic go through, in order? Give the list of the components in that order, from the "Billing batch" to the "Internet", both included, each an object whose keys are "component" and "zone".
2. "Zone a" of the "Paris region" fails entirely. Which subnets stop, and which keep running but lose their access to the "Internet"? Give an object whose keys are "stop" and "lose_internet", each the list of those subnets, each subnet an object whose keys are "vpc", "zone" and "subnet".
3. Which links have one end in the "Paris region" and the other in the "Frankfurt region"? Give the list of their labels.
4. The "Storefront API" of "Zone b" of the "Production VPC" writes an order with SQL, and this order later reaches the "Data warehouse" of the datacenter. Which components does it go through, in order? Give the list of the components in that order, from the "Storefront API" to the "Data warehouse", both included, each an object whose keys are "component" and "zone".
