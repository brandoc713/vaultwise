import { accounts, categories, statementImports, transactions } from "../data/fixtures";
import type { Account, Category, StatementImport, Transaction } from "../types";

const dataMode = import.meta.env.VITE_DATA_MODE ?? "fixtures";
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export function isApiMode() {
  return dataMode === "api";
}

export async function getAccounts(): Promise<Account[]> {
  if (!isApiMode()) {
    return accounts;
  }
  const response = await fetch(`${apiBaseUrl}/api/accounts`);
  if (!response.ok) throw new Error("Failed to load accounts");
  const rows = await response.json();
  return rows.map(mapAccount);
}

export async function getCategories(): Promise<Category[]> {
  if (!isApiMode()) {
    return categories;
  }
  const response = await fetch(`${apiBaseUrl}/api/categories`);
  if (!response.ok) throw new Error("Failed to load categories");
  const rows = await response.json();
  return rows.map(mapCategory);
}

export async function getTransactions(): Promise<Transaction[]> {
  if (!isApiMode()) {
    return transactions;
  }
  const response = await fetch(`${apiBaseUrl}/api/transactions`);
  if (!response.ok) throw new Error("Failed to load transactions");
  const rows = await response.json();
  return rows.map(mapTransaction);
}

export async function getStatementImports(): Promise<StatementImport[]> {
  if (!isApiMode()) {
    return statementImports;
  }
  const response = await fetch(`${apiBaseUrl}/api/statements`);
  if (!response.ok) throw new Error("Failed to load statement imports");
  const rows = await response.json();
  return rows.map(mapStatement);
}

export async function updateTransactionCategory(
  items: Transaction[],
  transactionId: string,
  categoryId: string,
): Promise<Transaction[]> {
  if (isApiMode()) {
    const response = await fetch(`${apiBaseUrl}/api/transactions/${transactionId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ category_id: categoryId, status: "reviewed" }),
    });
    if (!response.ok) throw new Error("Failed to update transaction");
    const updated = mapTransaction(await response.json());
    return items.map((item) => (item.id === transactionId ? updated : item));
  }
  return items.map((item) =>
    item.id === transactionId
      ? { ...item, categoryId, status: "reviewed" as const, manualOverride: true, confidence: 1 }
      : item,
  );
}

export async function downloadTransactionsCsv(items: Transaction[]) {
  if (isApiMode()) {
    const response = await fetch(`${apiBaseUrl}/api/transactions/export.csv`);
    if (!response.ok) throw new Error("Failed to export transactions");
    return response.text();
  }
  return exportTransactionsCsv(items);
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

function mapAccount(row: any): Account {
  return {
    id: row.id,
    name: row.name,
    institution: row.institution,
    type: row.account_type,
    lastFour: row.last_four ?? "",
  };
}

function mapCategory(row: any): Category {
  return {
    id: row.id,
    name: row.name,
    type: row.kind,
    color: row.color,
  };
}

function mapTransaction(row: any): Transaction {
  return {
    id: row.id,
    accountId: row.account_id,
    statementId: row.statement_id,
    date: row.date,
    postedDate: row.posted_date ?? row.date,
    description: row.description,
    merchant: row.merchant ?? "Unknown Merchant",
    amount: Number(row.amount),
    direction: row.direction,
    categoryId: row.category_id ?? "cat-uncat",
    confidence: Number(row.confidence),
    status: row.status,
    manualOverride: row.manual_override,
  };
}

function mapStatement(row: any): StatementImport {
  return {
    id: row.id,
    accountId: row.account_id,
    fileName: row.original_filename,
    fileType: row.file_type,
    importedAt: row.created_at,
    parsedCount: row.parsed_count,
    needsReviewCount: row.needs_review_count,
    duplicateCandidateCount: row.duplicate_candidate_count,
    status: row.parse_status === "parsed" ? "parsed" : row.parse_status === "failed" ? "failed" : "needs_review",
  };
}
