Read the file sources/1_data_model/<file>, which describes the data model of an online shop.
Do not open any other file of the current folder or of its subfolders, whether to read it or to search it.
Answer the four questions from this file alone, as one JSON object whose keys are "1", "2", "3" and "4".
Write each entity's name as the file writes it.

1. A customer returns an item of an order shipped in several parcels. Which entities must be crossed, in order, to go from RETURN_LINE to the warehouse the item left from? Give the list of the entities in that order, from RETURN_LINE to the last one, both included.
2. True or false? Give an object whose keys are "a", "b", "c" and "d", each true or false.
   a. A refund can exist without being attached to a return.
   b. One order line can be split across several parcels.
   c. One credit note can cover several invoices.
   d. One order can be paid by several payments.
3. Which entities hold a foreign key to VARIANT, and which hold a foreign key to ITEM? Give an object whose keys are "VARIANT" and "ITEM", each the list of the entities that hold a foreign key to it.
4. A seller of the marketplace receives a payout, from which commissions are deducted. Which entities must be crossed, in order, to go from SELLER_PAYOUT to the customers whose purchases generated these commissions? Give the list of the entities in that order, from SELLER_PAYOUT to the last one, both included.
