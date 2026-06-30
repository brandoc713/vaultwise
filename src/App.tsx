import { useMemo, useState } from "react";
import {
  ArrowDownToLine,
  BarChart3,
  CheckCircle2,
  Database,
  FileDown,
  FileSearch,
  Home,
  Layers3,
  Search,
  ShieldCheck,
  SlidersHorizontal,
  Upload,
  WalletCards,
} from "lucide-react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import {
  exportTransactionsCsv,
  getAccounts,
  getCategories,
  getStatementImports,
  getTransactions,
  updateTransactionCategory,
} from "./services/financeData";
import type { Category, Transaction, ViewKey } from "./types";

const navItems: Array<{ key: ViewKey; label: string; icon: typeof Home }> = [
  { key: "dashboard", label: "Dashboard", icon: BarChart3 },
  { key: "transactions", label: "Transactions", icon: WalletCards },
  { key: "review", label: "Statement Review", icon: FileSearch },
  { key: "categories", label: "Categories", icon: Layers3 },
  { key: "export", label: "Export", icon: FileDown },
];

const money = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

const exactMoney = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
});

function App() {
  const [activeView, setActiveView] = useState<ViewKey>("dashboard");
  const [transactions, setTransactions] = useState<Transaction[]>(getTransactions());
  const [query, setQuery] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");

  const accounts = getAccounts();
  const categories = getCategories();
  const statements = getStatementImports();

  const filteredTransactions = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    return transactions.filter((transaction) => {
      const matchesQuery =
        !normalizedQuery ||
        transaction.merchant.toLowerCase().includes(normalizedQuery) ||
        transaction.description.toLowerCase().includes(normalizedQuery);
      const matchesCategory = categoryFilter === "all" || transaction.categoryId === categoryFilter;
      const matchesStatus = statusFilter === "all" || transaction.status === statusFilter;
      return matchesQuery && matchesCategory && matchesStatus;
    });
  }, [categoryFilter, query, statusFilter, transactions]);

  function handleCategoryChange(transactionId: string, categoryId: string) {
    setTransactions((current) => updateTransactionCategory(current, transactionId, categoryId));
  }

  function handleExport() {
    const csv = exportTransactionsCsv(filteredTransactions);
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "normalized-transactions-demo.csv";
    link.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="min-h-screen bg-[#eef1ec] text-ink">
      <div className="flex min-h-screen">
        <aside className="hidden w-72 shrink-0 border-r border-line bg-white/75 px-5 py-6 lg:block">
          <div className="mb-8 flex items-center gap-3">
            <div className="grid h-11 w-11 place-items-center rounded-lg bg-ink text-white">
              <ShieldCheck size={23} />
            </div>
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.18em] text-moss">Local-first</p>
              <h1 className="text-xl font-semibold">Finance Intelligence</h1>
            </div>
          </div>

          <nav className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.key}
                  className={`nav-button ${activeView === item.key ? "nav-button-active" : ""}`}
                  onClick={() => setActiveView(item.key)}
                >
                  <Icon size={18} />
                  {item.label}
                </button>
              );
            })}
          </nav>

          <div className="mt-8 rounded-lg border border-line bg-panel p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.14em] text-bluegray">Demo state</p>
            <p className="mt-2 text-sm leading-6 text-slate-700">
              Synthetic household data only. The UI is wired through a service layer ready for FastAPI.
            </p>
          </div>
        </aside>

        <main className="min-w-0 flex-1 px-4 py-5 sm:px-6 lg:px-8">
          <MobileNav activeView={activeView} setActiveView={setActiveView} />
          <Header activeView={activeView} />

          {activeView === "dashboard" && (
            <Dashboard transactions={transactions} accounts={accounts} categories={categories} statements={statements} />
          )}
          {activeView === "transactions" && (
            <TransactionsView
              transactions={filteredTransactions}
              allTransactions={transactions}
              categories={categories}
              accounts={accounts}
              query={query}
              setQuery={setQuery}
              categoryFilter={categoryFilter}
              setCategoryFilter={setCategoryFilter}
              statusFilter={statusFilter}
              setStatusFilter={setStatusFilter}
              onCategoryChange={handleCategoryChange}
            />
          )}
          {activeView === "review" && (
            <ReviewView
              statements={statements}
              accounts={accounts}
              transactions={transactions}
              categories={categories}
              onCategoryChange={handleCategoryChange}
            />
          )}
          {activeView === "categories" && <CategoriesView categories={categories} transactions={transactions} />}
          {activeView === "export" && (
            <ExportView count={filteredTransactions.length} total={transactions.length} onExport={handleExport} />
          )}
        </main>
      </div>
    </div>
  );
}

function MobileNav({
  activeView,
  setActiveView,
}: {
  activeView: ViewKey;
  setActiveView: (view: ViewKey) => void;
}) {
  return (
    <div className="mb-4 rounded-lg border border-line bg-white p-2 shadow-soft lg:hidden">
      <div className="grid grid-cols-5 gap-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <button
              key={item.key}
              className={`grid h-12 place-items-center rounded-md ${activeView === item.key ? "bg-ink text-white" : "text-slate-600"}`}
              onClick={() => setActiveView(item.key)}
              title={item.label}
            >
              <Icon size={19} />
            </button>
          );
        })}
      </div>
    </div>
  );
}

function Header({ activeView }: { activeView: ViewKey }) {
  const titles: Record<ViewKey, { title: string; subtitle: string }> = {
    dashboard: {
      title: "Household finance dashboard",
      subtitle: "Normalized statements, category intelligence, and review workflows in one local-first workspace.",
    },
    transactions: {
      title: "Transaction review",
      subtitle: "Search, filter, and correct normalized transactions before exporting clean records.",
    },
    review: {
      title: "Statement ingestion",
      subtitle: "A recruiter-visible preview of the PDF and CSV import workflow planned for the backend.",
    },
    categories: {
      title: "Rules-first categorization",
      subtitle: "Transparent merchant normalization and confidence scoring before ML is introduced.",
    },
    export: {
      title: "Clean data export",
      subtitle: "Download normalized demo transactions using the same schema intended for backend storage.",
    },
  };

  return (
    <header className="mb-6 flex flex-col justify-between gap-4 rounded-lg border border-line bg-white p-5 shadow-soft sm:flex-row sm:items-center">
      <div>
        <p className="mb-1 text-xs font-semibold uppercase tracking-[0.16em] text-moss">Personal Finance Statement Intelligence</p>
        <h2 className="text-2xl font-semibold">{titles[activeView].title}</h2>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">{titles[activeView].subtitle}</p>
      </div>
      <div className="flex items-center gap-2 rounded-lg border border-line bg-panel px-3 py-2 text-sm text-slate-700">
        <Database size={16} />
        Static MVP / synthetic data
      </div>
    </header>
  );
}

function Dashboard({
  transactions,
  accounts,
  categories,
  statements,
}: {
  transactions: Transaction[];
  accounts: ReturnType<typeof getAccounts>;
  categories: Category[];
  statements: ReturnType<typeof getStatementImports>;
}) {
  const income = transactions.filter((t) => t.direction === "income").reduce((sum, t) => sum + t.amount, 0);
  const expenses = Math.abs(
    transactions.filter((t) => t.direction === "expense").reduce((sum, t) => sum + t.amount, 0),
  );
  const net = income - expenses;
  const reviewCount = transactions.filter((t) => t.status !== "reviewed").length;
  const categoryTotals = getCategoryTotals(transactions, categories);
  const monthly = getMonthlyTrend(transactions);
  const topCategory = categoryTotals[0];

  return (
    <section className="space-y-5">
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Income tracked" value={money.format(income)} detail="Across checking and deposits" />
        <MetricCard label="Spending tracked" value={money.format(expenses)} detail="Excludes transfers and investments" />
        <MetricCard label="Net cash flow" value={money.format(net)} detail="Three-month demo window" />
        <MetricCard label="Needs review" value={`${reviewCount}`} detail="Low confidence or ambiguous rows" tone="warning" />
      </div>

      <div className="grid gap-5 xl:grid-cols-[1.15fr_0.85fr]">
        <Panel title="Monthly cash flow" action="Apr-Jun 2026">
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={monthly}>
                <CartesianGrid stroke="#dce3dc" vertical={false} />
                <XAxis dataKey="month" tickLine={false} axisLine={false} />
                <YAxis tickFormatter={(value) => `$${Number(value) / 1000}k`} tickLine={false} axisLine={false} />
                <Tooltip formatter={formatTooltipMoney} />
                <Area type="monotone" dataKey="income" stroke="#2f855a" fill="#cfe7d7" strokeWidth={2} />
                <Area type="monotone" dataKey="expenses" stroke="#9a6048" fill="#ead2c5" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Panel>

        <Panel title="Spending by category" action={topCategory ? `Top: ${topCategory.name}` : "No expenses"}>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={categoryTotals.slice(0, 7)}>
                <CartesianGrid stroke="#dce3dc" vertical={false} />
                <XAxis dataKey="name" tickLine={false} axisLine={false} tick={{ fontSize: 12 }} />
                <YAxis tickFormatter={(value) => `$${Number(value) / 1000}k`} tickLine={false} axisLine={false} />
                <Tooltip formatter={formatTooltipMoney} />
                <Bar dataKey="total" radius={[4, 4, 0, 0]}>
                  {categoryTotals.slice(0, 7).map((entry) => (
                    <Cell key={entry.id} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>
      </div>

      <div className="grid gap-5 xl:grid-cols-[1fr_0.8fr]">
        <Panel title="Recent normalized transactions" action={`${transactions.length} demo rows`}>
          <TransactionTable
            transactions={transactions.slice(-8).reverse()}
            categories={categories}
            accounts={accounts}
            compact
          />
        </Panel>
        <Panel title="Statement health" action={`${statements.length} imports`}>
          <div className="space-y-3">
            {statements.map((statement) => (
              <div key={statement.id} className="rounded-lg border border-line bg-panel p-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="font-medium">{statement.fileName}</p>
                    <p className="mt-1 text-sm text-slate-600">{accountName(statement.accountId, accounts)}</p>
                  </div>
                  <StatusBadge status={statement.status === "parsed" ? "reviewed" : "needs_review"} />
                </div>
                <div className="mt-3 grid grid-cols-3 gap-2 text-center text-sm">
                  <MiniStat label="Parsed" value={statement.parsedCount} />
                  <MiniStat label="Review" value={statement.needsReviewCount} />
                  <MiniStat label="Dupes" value={statement.duplicateCandidateCount} />
                </div>
              </div>
            ))}
          </div>
        </Panel>
      </div>
    </section>
  );
}

function TransactionsView({
  transactions,
  allTransactions,
  categories,
  accounts,
  query,
  setQuery,
  categoryFilter,
  setCategoryFilter,
  statusFilter,
  setStatusFilter,
  onCategoryChange,
}: {
  transactions: Transaction[];
  allTransactions: Transaction[];
  categories: Category[];
  accounts: ReturnType<typeof getAccounts>;
  query: string;
  setQuery: (value: string) => void;
  categoryFilter: string;
  setCategoryFilter: (value: string) => void;
  statusFilter: string;
  setStatusFilter: (value: string) => void;
  onCategoryChange: (transactionId: string, categoryId: string) => void;
}) {
  const reviewCount = allTransactions.filter((transaction) => transaction.status !== "reviewed").length;
  return (
    <section className="space-y-5">
      <div className="grid gap-4 md:grid-cols-3">
        <MetricCard label="Visible rows" value={`${transactions.length}`} detail="After active filters" />
        <MetricCard label="Manual corrections" value={`${allTransactions.filter((t) => t.manualOverride).length}`} detail="Captured for future training" />
        <MetricCard label="Review queue" value={`${reviewCount}`} detail="Confidence below target" tone="warning" />
      </div>

      <Panel title="Filters" action="Local UI state">
        <div className="grid gap-3 lg:grid-cols-[1fr_220px_180px]">
          <label className="relative block">
            <Search className="pointer-events-none absolute left-3 top-3 text-slate-400" size={18} />
            <input
              className="input pl-10"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search merchant or description"
            />
          </label>
          <select className="input" value={categoryFilter} onChange={(event) => setCategoryFilter(event.target.value)}>
            <option value="all">All categories</option>
            {categories.map((category) => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>
          <select className="input" value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>
            <option value="all">All statuses</option>
            <option value="reviewed">Reviewed</option>
            <option value="needs_review">Needs review</option>
            <option value="flagged">Flagged</option>
          </select>
        </div>
      </Panel>

      <Panel title="Normalized transactions" action="Editable categories">
        <TransactionTable
          transactions={transactions}
          categories={categories}
          accounts={accounts}
          onCategoryChange={onCategoryChange}
        />
      </Panel>
    </section>
  );
}

function ReviewView({
  statements,
  accounts,
  transactions,
  categories,
  onCategoryChange,
}: {
  statements: ReturnType<typeof getStatementImports>;
  accounts: ReturnType<typeof getAccounts>;
  transactions: Transaction[];
  categories: Category[];
  onCategoryChange: (transactionId: string, categoryId: string) => void;
}) {
  const queue = transactions.filter((transaction) => transaction.status !== "reviewed");
  return (
    <section className="grid gap-5 xl:grid-cols-[0.8fr_1.2fr]">
      <div className="space-y-5">
        <Panel title="Upload statement" action="Demo preview">
          <div className="rounded-lg border-2 border-dashed border-line bg-panel p-8 text-center">
            <div className="mx-auto grid h-12 w-12 place-items-center rounded-lg bg-white text-moss shadow-soft">
              <Upload size={22} />
            </div>
            <h3 className="mt-4 text-lg font-semibold">Drop a PDF or CSV statement</h3>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              The MVP shows the intended workflow with synthetic parsed rows. FastAPI parsing is the next implementation step.
            </p>
            <button className="mt-5 inline-flex items-center gap-2 rounded-md bg-ink px-4 py-2 text-sm font-medium text-white">
              <ArrowDownToLine size={16} />
              Stage demo import
            </button>
          </div>
        </Panel>

        <Panel title="Recent imports" action="Traceable sources">
          <div className="space-y-3">
            {statements.map((statement) => (
              <div key={statement.id} className="rounded-lg border border-line bg-white p-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="font-medium">{statement.fileName}</p>
                    <p className="mt-1 text-sm text-slate-600">
                      {statement.fileType.toUpperCase()} / {accountName(statement.accountId, accounts)}
                    </p>
                  </div>
                  <StatusBadge status={statement.status === "parsed" ? "reviewed" : "needs_review"} />
                </div>
              </div>
            ))}
          </div>
        </Panel>
      </div>

      <Panel title="Human-in-the-loop queue" action={`${queue.length} rows`}>
        <TransactionTable
          transactions={queue}
          categories={categories}
          accounts={accounts}
          onCategoryChange={onCategoryChange}
        />
      </Panel>
    </section>
  );
}

function CategoriesView({ categories, transactions }: { categories: Category[]; transactions: Transaction[] }) {
  const totals = getCategoryTotals(transactions, categories);
  const rules = [
    ["KROGER #4481", "Kroger", "Groceries", "0.94"],
    ["AMZN MKTP", "Amazon", "Shopping", "0.70"],
    ["ACH TRANSFER", "Bank Transfer", "Transfers", "0.98"],
    ["DUKE ENERGY", "Duke Energy", "Utilities", "0.93"],
    ["AUTO LOAN", "Demo Auto Finance", "Loans", "0.89"],
  ];

  return (
    <section className="grid gap-5 xl:grid-cols-[0.95fr_1.05fr]">
      <Panel title="Category coverage" action={`${categories.length} categories`}>
        <div className="grid gap-3 sm:grid-cols-2">
          {categories.map((category) => {
            const total = totals.find((item) => item.id === category.id)?.total ?? 0;
            return (
              <div key={category.id} className="rounded-lg border border-line bg-panel p-4">
                <div className="flex items-center gap-3">
                  <span className="h-3 w-3 rounded-full" style={{ backgroundColor: category.color }} />
                  <div>
                    <p className="font-medium">{category.name}</p>
                    <p className="mt-1 text-sm text-slate-600">{category.type}</p>
                  </div>
                </div>
                <p className="mt-3 text-xl font-semibold">{money.format(total)}</p>
              </div>
            );
          })}
        </div>
      </Panel>

      <Panel title="Merchant normalization rules" action="Rules baseline">
        <div className="overflow-hidden rounded-lg border border-line">
          <table className="min-w-full divide-y divide-line text-sm">
            <thead className="bg-panel text-left text-xs uppercase tracking-[0.12em] text-slate-500">
              <tr>
                <th className="px-4 py-3">Raw text</th>
                <th className="px-4 py-3">Merchant</th>
                <th className="px-4 py-3">Category</th>
                <th className="px-4 py-3">Confidence</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line bg-white">
              {rules.map(([raw, merchant, category, confidence]) => (
                <tr key={raw}>
                  <td className="px-4 py-3 font-mono text-xs text-slate-700">{raw}</td>
                  <td className="px-4 py-3">{merchant}</td>
                  <td className="px-4 py-3">{category}</td>
                  <td className="px-4 py-3">{confidence}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="mt-4 rounded-lg border border-line bg-panel p-4 text-sm leading-6 text-slate-700">
          Corrections made in the review queue are marked as manual overrides. The next backend phase will persist those labels as
          training data for a scikit-learn classifier.
        </div>
      </Panel>
    </section>
  );
}

function ExportView({ count, total, onExport }: { count: number; total: number; onExport: () => void }) {
  return (
    <section className="grid gap-5 xl:grid-cols-[0.8fr_1.2fr]">
      <Panel title="CSV export" action="Functional demo">
        <div className="rounded-lg border border-line bg-panel p-5">
          <FileDown size={28} className="text-moss" />
          <h3 className="mt-4 text-xl font-semibold">Download normalized transactions</h3>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            Exports the current demo transaction state, including category corrections made during this browser session.
          </p>
          <button
            className="mt-5 inline-flex items-center gap-2 rounded-md bg-ink px-4 py-2 text-sm font-medium text-white"
            onClick={onExport}
          >
            <FileDown size={16} />
            Export {count} visible rows
          </button>
        </div>
      </Panel>

      <Panel title="Normalized schema" action={`${total} records loaded`}>
        <div className="grid gap-3 sm:grid-cols-2">
          {[
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
          ].map((field) => (
            <div key={field} className="rounded-md border border-line bg-panel px-3 py-2 font-mono text-sm text-slate-700">
              {field}
            </div>
          ))}
        </div>
      </Panel>
    </section>
  );
}

function TransactionTable({
  transactions,
  categories,
  accounts,
  onCategoryChange,
  compact = false,
}: {
  transactions: Transaction[];
  categories: Category[];
  accounts: ReturnType<typeof getAccounts>;
  onCategoryChange?: (transactionId: string, categoryId: string) => void;
  compact?: boolean;
}) {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-line text-sm">
        <thead className="bg-panel text-left text-xs uppercase tracking-[0.12em] text-slate-500">
          <tr>
            <th className="px-4 py-3">Date</th>
            <th className="px-4 py-3">Merchant</th>
            {!compact && <th className="px-4 py-3">Account</th>}
            <th className="px-4 py-3">Amount</th>
            <th className="px-4 py-3">Category</th>
            {!compact && <th className="px-4 py-3">Confidence</th>}
            <th className="px-4 py-3">Status</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-line bg-white">
          {transactions.map((transaction) => {
            const category = categories.find((item) => item.id === transaction.categoryId);
            return (
              <tr key={transaction.id} className={transaction.status === "flagged" ? "bg-red-50/60" : undefined}>
                <td className="whitespace-nowrap px-4 py-3 text-slate-600">{transaction.date}</td>
                <td className="min-w-56 px-4 py-3">
                  <p className="font-medium">{transaction.merchant}</p>
                  {!compact && <p className="mt-1 max-w-sm truncate text-xs text-slate-500">{transaction.description}</p>}
                </td>
                {!compact && <td className="whitespace-nowrap px-4 py-3 text-slate-600">{accountName(transaction.accountId, accounts)}</td>}
                <td className={`whitespace-nowrap px-4 py-3 font-semibold ${transaction.amount >= 0 ? "text-green-700" : "text-slate-800"}`}>
                  {exactMoney.format(transaction.amount)}
                </td>
                <td className="min-w-44 px-4 py-3">
                  {onCategoryChange ? (
                    <select
                      className="w-full rounded-md border border-line bg-white px-2 py-1.5 text-sm"
                      value={transaction.categoryId}
                      onChange={(event) => onCategoryChange(transaction.id, event.target.value)}
                    >
                      {categories.map((item) => (
                        <option key={item.id} value={item.id}>
                          {item.name}
                        </option>
                      ))}
                    </select>
                  ) : (
                    <span className="inline-flex items-center gap-2">
                      <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: category?.color }} />
                      {category?.name}
                    </span>
                  )}
                </td>
                {!compact && <td className="whitespace-nowrap px-4 py-3">{Math.round(transaction.confidence * 100)}%</td>}
                <td className="whitespace-nowrap px-4 py-3">
                  <StatusBadge status={transaction.status} />
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
      {transactions.length === 0 && (
        <div className="rounded-b-lg border-x border-b border-line bg-white p-8 text-center text-sm text-slate-600">
          No transactions match the current filters.
        </div>
      )}
    </div>
  );
}

function MetricCard({
  label,
  value,
  detail,
  tone = "default",
}: {
  label: string;
  value: string;
  detail: string;
  tone?: "default" | "warning";
}) {
  return (
    <div className="rounded-lg border border-line bg-white p-5 shadow-soft">
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium text-slate-600">{label}</p>
        {tone === "warning" ? <SlidersHorizontal size={17} className="text-clay" /> : <CheckCircle2 size={17} className="text-moss" />}
      </div>
      <p className="mt-3 text-3xl font-semibold">{value}</p>
      <p className="mt-2 text-sm text-slate-500">{detail}</p>
    </div>
  );
}

function Panel({ title, action, children }: { title: string; action: string; children: React.ReactNode }) {
  return (
    <section className="rounded-lg border border-line bg-white p-5 shadow-soft">
      <div className="mb-4 flex items-center justify-between gap-4">
        <h3 className="text-lg font-semibold">{title}</h3>
        <span className="rounded-md border border-line bg-panel px-2.5 py-1 text-xs font-medium text-slate-600">{action}</span>
      </div>
      {children}
    </section>
  );
}

function StatusBadge({ status }: { status: Transaction["status"] }) {
  const label = status === "needs_review" ? "Needs review" : status === "flagged" ? "Flagged" : "Reviewed";
  const className =
    status === "reviewed"
      ? "bg-green-50 text-green-700 ring-green-200"
      : status === "flagged"
        ? "bg-red-50 text-red-700 ring-red-200"
        : "bg-amber-50 text-amber-700 ring-amber-200";
  return <span className={`inline-flex rounded-md px-2 py-1 text-xs font-medium ring-1 ${className}`}>{label}</span>;
}

function MiniStat({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-md bg-white p-2">
      <p className="text-lg font-semibold">{value}</p>
      <p className="text-xs text-slate-500">{label}</p>
    </div>
  );
}

function accountName(accountId: string, accounts: ReturnType<typeof getAccounts>) {
  return accounts.find((account) => account.id === accountId)?.name ?? "Unknown account";
}

function getCategoryTotals(transactions: Transaction[], categories: Category[]) {
  return categories
    .map((category) => {
      const total = Math.abs(
        transactions
          .filter((transaction) => transaction.categoryId === category.id && transaction.direction === "expense")
          .reduce((sum, transaction) => sum + transaction.amount, 0),
      );
      return { ...category, total };
    })
    .filter((category) => category.total > 0)
    .sort((a, b) => b.total - a.total);
}

function getMonthlyTrend(transactions: Transaction[]) {
  const months = ["2026-04", "2026-05", "2026-06"];
  return months.map((month) => {
    const rows = transactions.filter((transaction) => transaction.date.startsWith(month));
    const income = rows.filter((row) => row.direction === "income").reduce((sum, row) => sum + row.amount, 0);
    const expenses = Math.abs(rows.filter((row) => row.direction === "expense").reduce((sum, row) => sum + row.amount, 0));
    return { month: new Date(`${month}-02`).toLocaleString("en-US", { month: "short" }), income, expenses };
  });
}

function formatTooltipMoney(value: unknown) {
  const amount = typeof value === "number" ? value : Number(value ?? 0);
  return exactMoney.format(amount);
}

export default App;
