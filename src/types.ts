export type TransactionDirection = "income" | "expense" | "transfer";
export type TransactionStatus = "reviewed" | "needs_review" | "flagged";

export interface Account {
  id: string;
  name: string;
  institution: string;
  type: "checking" | "savings" | "credit" | "loan" | "investment";
  lastFour: string;
}

export interface Category {
  id: string;
  name: string;
  type: "income" | "expense" | "transfer" | "loan" | "investment";
  color: string;
}

export interface Transaction {
  id: string;
  accountId: string;
  statementId: string;
  date: string;
  postedDate: string;
  description: string;
  merchant: string;
  amount: number;
  direction: TransactionDirection;
  categoryId: string;
  confidence: number;
  status: TransactionStatus;
  manualOverride: boolean;
}

export interface StatementImport {
  id: string;
  accountId: string;
  fileName: string;
  fileType: "pdf" | "csv";
  importedAt: string;
  parsedCount: number;
  needsReviewCount: number;
  duplicateCandidateCount: number;
  status: "parsed" | "needs_review" | "failed";
}

export type ViewKey = "dashboard" | "transactions" | "review" | "categories" | "export";
