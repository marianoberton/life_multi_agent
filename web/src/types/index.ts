export interface Transaction {
  id: string;
  created_at: string;
  date_transaction: string | null;
  amount: number;
  currency: 'ARS' | 'USD' | string | null;
  category: string | null;
  subcategory: string | null;
  merchant: string | null;
  payment_method: string | null;
  is_fixed: boolean | null;
  is_client_expense: boolean | null;
  installment_current: number | null;
  installment_total: number | null;
  source: string | null;
}

export interface JournalEntry {
  id: string;
  created_at: string;
  content: string | null;
  mood_score: number | null;
  sentiment_tags: string[] | null;
  embedding: number[] | string | null; // vector(1536)
}

export interface Activity {
  id: string;
  created_at: string;
  type: string | null;
  details: Record<string, any> | null; // jsonb
}
