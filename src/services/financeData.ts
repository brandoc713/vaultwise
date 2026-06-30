import { accounts, categories, statementImports, transactions } from "../data/fixtures";
import type { Transaction } from "../types";

export function getAccounts() {
  return accounts;
}

export function getCategories() {
  return categories;
}

export function getTransactions() {
  return transactions;
}

export function getStatementImports() {
  return statementImports;
}

export function updateTransactionCategory(
  items: Transaction[],
  transactionId: string,
  categoryId: string,
) {
  return items.map((item) =>
    item.id === transactionId
      ? { ...item, categoryId, status: "reviewed" as const, manualOverride: true, confidence: 1 }
      : item,
  );
}

export function exportTransactionsCsv(items: Transaction[]) {
  const header = [
    "transaction_id",
    "account_id",
    "statement_id",
    "date",
    "posted_date",
    "description",
    "merchant",
    "amount",
    "direction",
    "category_id",
    "confidence",
    "status",
    "manual_override",
  ];

  const rows = items.map((item) =>
    [
      item.id,
      item.accountId,
      item.statementId,
      item.date,
      item.postedDate,
      item.description,
      item.merchant,
      item.amount.toFixed(2),
      item.direction,
      item.categoryId,
      item.confidence.toFixed(2),
      item.status,
      item.manualOverride ? "true" : "false",
    ].map(csvEscape).join(","),
  );

  return [header.join(","), ...rows].join("\n");
}

function csvEscape(value: string) {
  if (/[",\n]/.test(value)) {
    return `"${value.replace(/"/g, '""')}"`;
  }
  return value;
}
