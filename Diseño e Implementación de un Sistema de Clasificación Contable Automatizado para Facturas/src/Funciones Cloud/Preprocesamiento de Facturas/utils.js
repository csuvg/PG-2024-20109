function modifyInvoice(invoice, position) { 
    return invoice.items.map(item => ({
        initial_description: item.initial_description,
        final_description: item.accounting_specifications[position].final_description,
        unit_total: parseFloat(item.total) / parseFloat(item.quantity),
        company_tid: position === 'in' ? invoice.receptor_id : invoice.sender_id,
        invoice_type: invoice.type,
        accounting_classification: item.accounting_specifications[position].accounting_classification,
        analytic_classification: item.accounting_specifications[position].analytic_classification,
        establishment_id: invoice.establishment_id,
        establishment_name: invoice.establishment_name
    }));
}

module.exports = {
    modifyInvoice
}