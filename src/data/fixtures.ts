import type { Account, Category, StatementImport, Transaction } from "../types";

export const accounts: Account[] = [
  { id: "acc-checking", name: "Household Checking", institution: "Local Credit Union", type: "checking", lastFour: "1042" },
  { id: "acc-savings", name: "Emergency Savings", institution: "Local Credit Union", type: "savings", lastFour: "7781" },
  { id: "acc-card", name: "Everyday Rewards Card", institution: "Demo Card Services", type: "credit", lastFour: "4420" },
  { id: "acc-invest", name: "Family Brokerage", institution: "Self-Hosted Import", type: "investment", lastFour: "9001" },
];

export const categories: Category[] = [
  { id: "cat-income", name: "Income", type: "income", color: "#2f855a" },
  { id: "cat-groceries", name: "Groceries", type: "expense", color: "#536f56" },
  { id: "cat-housing", name: "Housing", type: "expense", color: "#9a6048" },
  { id: "cat-utilities", name: "Utilities", type: "expense", color: "#526b7a" },
  { id: "cat-dining", name: "Dining", type: "expense", color: "#b06b36" },
  { id: "cat-transport", name: "Transportation", type: "expense", color: "#5c6f91" },
  { id: "cat-health", name: "Health", type: "expense", color: "#7c5f82" },
  { id: "cat-shopping", name: "Shopping", type: "expense", color: "#8a6f3d" },
  { id: "cat-fees", name: "Fees", type: "expense", color: "#8b4d4d" },
  { id: "cat-transfer", name: "Transfers", type: "transfer", color: "#4f6f7a" },
  { id: "cat-loan", name: "Loans", type: "loan", color: "#735f4b" },
  { id: "cat-invest", name: "Investments", type: "investment", color: "#476a62" },
  { id: "cat-uncat", name: "Uncategorized", type: "expense", color: "#6b7280" },
];

const baseTransactions: Omit<Transaction, "id" | "statementId">[] = [
  { accountId: "acc-checking", date: "2026-04-01", postedDate: "2026-04-01", description: "ACME PAYROLL ACH CREDIT", merchant: "Acme Payroll", amount: 5200, direction: "income", categoryId: "cat-income", confidence: 0.99, status: "reviewed", manualOverride: false },
  { accountId: "acc-checking", date: "2026-04-02", postedDate: "2026-04-02", description: "RENT PAYMENT AUTOPAY", merchant: "Oak Street Homes", amount: -1875, direction: "expense", categoryId: "cat-housing", confidence: 0.96, status: "reviewed", manualOverride: false },
  { accountId: "acc-card", date: "2026-04-03", postedDate: "2026-04-04", description: "KROGER #4481 CINCINNATI OH", merchant: "Kroger", amount: -142.33, direction: "expense", categoryId: "cat-groceries", confidence: 0.94, status: "reviewed", manualOverride: false },
  { accountId: "acc-card", date: "2026-04-05", postedDate: "2026-04-06", description: "AMZN MKTP US*9T2Q", merchant: "Amazon", amount: -76.12, direction: "expense", categoryId: "cat-shopping", confidence: 0.71, status: "needs_review", manualOverride: false },
  { accountId: "acc-checking", date: "2026-04-07", postedDate: "2026-04-07", description: "DUKE ENERGY BILLPAY", merchant: "Duke Energy", amount: -184.44, direction: "expense", categoryId: "cat-utilities", confidence: 0.93, status: "reviewed", manualOverride: false },
  { accountId: "acc-card", date: "2026-04-08", postedDate: "2026-04-09", description: "SHELL OIL 5742", merchant: "Shell", amount: -52.88, direction: "expense", categoryId: "cat-transport", confidence: 0.91, status: "reviewed", manualOverride: false },
  { accountId: "acc-card", date: "2026-04-10", postedDate: "2026-04-11", description: "NETFLIX.COM", merchant: "Netflix", amount: -22.99, direction: "expense", categoryId: "cat-uncat", confidence: 0.46, status: "flagged", manualOverride: false },
  { accountId: "acc-checking", date: "2026-04-12", postedDate: "2026-04-12", description: "ACH TRANSFER TO SAVINGS", merchant: "Bank Transfer", amount: -600, direction: "transfer", categoryId: "cat-transfer", confidence: 0.98, status: "reviewed", manualOverride: false },
  { accountId: "acc-savings", date: "2026-04-12", postedDate: "2026-04-12", description: "ACH TRANSFER FROM CHECKING", merchant: "Bank Transfer", amount: 600, direction: "transfer", categoryId: "cat-transfer", confidence: 0.98, status: "reviewed", manualOverride: false },
  { accountId: "acc-checking", date: "2026-04-15", postedDate: "2026-04-15", description: "ACME PAYROLL ACH CREDIT", merchant: "Acme Payroll", amount: 5200, direction: "income", categoryId: "cat-income", confidence: 0.99, status: "reviewed", manualOverride: false },
  { accountId: "acc-checking", date: "2026-04-16", postedDate: "2026-04-16", description: "AUTO LOAN PAYMENT", merchant: "Demo Auto Finance", amount: -415.2, direction: "expense", categoryId: "cat-loan", confidence: 0.89, status: "reviewed", manualOverride: false },
  { accountId: "acc-invest", date: "2026-04-18", postedDate: "2026-04-18", description: "BROKERAGE CONTRIBUTION", merchant: "Family Brokerage", amount: -350, direction: "transfer", categoryId: "cat-invest", confidence: 0.87, status: "reviewed", manualOverride: false },
  { accountId: "acc-card", date: "2026-04-20", postedDate: "2026-04-21", description: "BLUEBIRD CAFE", merchant: "Bluebird Cafe", amount: -48.64, direction: "expense", categoryId: "cat-dining", confidence: 0.84, status: "reviewed", manualOverride: false },
  { accountId: "acc-checking", date: "2026-04-24", postedDate: "2026-04-24", description: "WATER UTILITY PAYMENT", merchant: "City Water", amount: -69.31, direction: "expense", categoryId: "cat-utilities", confidence: 0.9, status: "reviewed", manualOverride: false },
  { accountId: "acc-card", date: "2026-04-27", postedDate: "2026-04-28", description: "TARGET T-1182", merchant: "Target", amount: -118.21, direction: "expense", categoryId: "cat-shopping", confidence: 0.67, status: "needs_review", manualOverride: false },
];

const mayJune: Omit<Transaction, "id" | "statementId">[] = [
  { accountId: "acc-checking", date: "2026-05-01", postedDate: "2026-05-01", description: "ACME PAYROLL ACH CREDIT", merchant: "Acme Payroll", amount: 5200, direction: "income", categoryId: "cat-income", confidence: 0.99, status: "reviewed", manualOverride: false },
  { accountId: "acc-checking", date: "2026-05-02", postedDate: "2026-05-02", description: "RENT PAYMENT AUTOPAY", merchant: "Oak Street Homes", amount: -1875, direction: "expense", categoryId: "cat-housing", confidence: 0.96, status: "reviewed", manualOverride: false },
  { accountId: "acc-card", date: "2026-05-04", postedDate: "2026-05-05", description: "WHOLEFDS CIN 1021", merchant: "Whole Foods", amount: -166.87, direction: "expense", categoryId: "cat-groceries", confidence: 0.88, status: "reviewed", manualOverride: false },
  { accountId: "acc-card", date: "2026-05-06", postedDate: "2026-05-07", description: "UBER TRIP HELP.UBER.COM", merchant: "Uber", amount: -34.18, direction: "expense", categoryId: "cat-transport", confidence: 0.86, status: "reviewed", manualOverride: false },
  { accountId: "acc-checking", date: "2026-05-09", postedDate: "2026-05-09", description: "MOBILE DEPOSIT", merchant: "Mobile Deposit", amount: 240, direction: "income", categoryId: "cat-income", confidence: 0.76, status: "needs_review", manualOverride: false },
  { accountId: "acc-card", date: "2026-05-12", postedDate: "2026-05-13", description: "CVS PHARMACY 3142", merchant: "CVS Pharmacy", amount: -28.74, direction: "expense", categoryId: "cat-health", confidence: 0.81, status: "reviewed", manualOverride: false },
  { accountId: "acc-checking", date: "2026-05-15", postedDate: "2026-05-15", description: "ACME PAYROLL ACH CREDIT", merchant: "Acme Payroll", amount: 5200, direction: "income", categoryId: "cat-income", confidence: 0.99, status: "reviewed", manualOverride: false },
  { accountId: "acc-card", date: "2026-05-18", postedDate: "2026-05-19", description: "SQ *LOCAL PIZZA", merchant: "Local Pizza", amount: -61.5, direction: "expense", categoryId: "cat-dining", confidence: 0.79, status: "needs_review", manualOverride: false },
  { accountId: "acc-checking", date: "2026-05-20", postedDate: "2026-05-20", description: "CREDIT CARD PAYMENT", merchant: "Demo Card Services", amount: -1230.44, direction: "transfer", categoryId: "cat-transfer", confidence: 0.92, status: "reviewed", manualOverride: false },
  { accountId: "acc-card", date: "2026-05-22", postedDate: "2026-05-23", description: "SERVICE FEE", merchant: "Demo Card Services", amount: -9.95, direction: "expense", categoryId: "cat-fees", confidence: 0.83, status: "reviewed", manualOverride: false },
  { accountId: "acc-checking", date: "2026-06-01", postedDate: "2026-06-01", description: "ACME PAYROLL ACH CREDIT", merchant: "Acme Payroll", amount: 5200, direction: "income", categoryId: "cat-income", confidence: 0.99, status: "reviewed", manualOverride: false },
  { accountId: "acc-checking", date: "2026-06-02", postedDate: "2026-06-02", description: "RENT PAYMENT AUTOPAY", merchant: "Oak Street Homes", amount: -1875, direction: "expense", categoryId: "cat-housing", confidence: 0.96, status: "reviewed", manualOverride: false },
  { accountId: "acc-card", date: "2026-06-04", postedDate: "2026-06-05", description: "KROGER #4481 CINCINNATI OH", merchant: "Kroger", amount: -151.22, direction: "expense", categoryId: "cat-groceries", confidence: 0.94, status: "reviewed", manualOverride: false },
  { accountId: "acc-card", date: "2026-06-07", postedDate: "2026-06-08", description: "UNKNOWN POS 88210", merchant: "Unknown POS", amount: -43.19, direction: "expense", categoryId: "cat-uncat", confidence: 0.31, status: "flagged", manualOverride: false },
  { accountId: "acc-checking", date: "2026-06-10", postedDate: "2026-06-10", description: "INTERNET BILLPAY", merchant: "FiberNet", amount: -82.0, direction: "expense", categoryId: "cat-utilities", confidence: 0.91, status: "reviewed", manualOverride: false },
  { accountId: "acc-card", date: "2026-06-13", postedDate: "2026-06-14", description: "TRADER JOE'S #671", merchant: "Trader Joe's", amount: -98.71, direction: "expense", categoryId: "cat-groceries", confidence: 0.9, status: "reviewed", manualOverride: false },
  { accountId: "acc-checking", date: "2026-06-15", postedDate: "2026-06-15", description: "ACME PAYROLL ACH CREDIT", merchant: "Acme Payroll", amount: 5200, direction: "income", categoryId: "cat-income", confidence: 0.99, status: "reviewed", manualOverride: false },
  { accountId: "acc-invest", date: "2026-06-18", postedDate: "2026-06-18", description: "BROKERAGE CONTRIBUTION", merchant: "Family Brokerage", amount: -500, direction: "transfer", categoryId: "cat-invest", confidence: 0.87, status: "reviewed", manualOverride: false },
  { accountId: "acc-card", date: "2026-06-21", postedDate: "2026-06-22", description: "AMZN MKTP US*3L7R", merchant: "Amazon", amount: -129.48, direction: "expense", categoryId: "cat-shopping", confidence: 0.7, status: "needs_review", manualOverride: false },
  { accountId: "acc-card", date: "2026-06-25", postedDate: "2026-06-26", description: "HOSPITAL PARKING", merchant: "Hospital Parking", amount: -12, direction: "expense", categoryId: "cat-health", confidence: 0.63, status: "needs_review", manualOverride: false },
];

export const transactions: Transaction[] = [...baseTransactions, ...mayJune].map((transaction, index) => ({
  ...transaction,
  id: `txn-${String(index + 1).padStart(3, "0")}`,
  statementId: index < 15 ? "stmt-apr" : index < 25 ? "stmt-may" : "stmt-jun",
}));

export const statementImports: StatementImport[] = [
  { id: "stmt-apr", accountId: "acc-checking", fileName: "checking-april-2026.pdf", fileType: "pdf", importedAt: "2026-06-26T14:20:00Z", parsedCount: 15, needsReviewCount: 3, duplicateCandidateCount: 1, status: "needs_review" },
  { id: "stmt-may", accountId: "acc-card", fileName: "rewards-card-may-2026.csv", fileType: "csv", importedAt: "2026-06-27T16:42:00Z", parsedCount: 10, needsReviewCount: 2, duplicateCandidateCount: 0, status: "parsed" },
  { id: "stmt-jun", accountId: "acc-checking", fileName: "household-june-2026.pdf", fileType: "pdf", importedAt: "2026-06-29T09:12:00Z", parsedCount: 10, needsReviewCount: 4, duplicateCandidateCount: 1, status: "needs_review" },
];
