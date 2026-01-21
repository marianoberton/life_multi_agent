import { supabase } from './supabase';
import { Transaction, JournalEntry, Activity } from '@/types';
import { format, subDays, startOfMonth, endOfMonth } from 'date-fns';

export async function getDashboardData() {
  const now = new Date();
  const startMonth = startOfMonth(now).toISOString();
  const endMonth = endOfMonth(now).toISOString();
  const sevenDaysAgo = subDays(now, 7).toISOString();

  // 1. Fetch Finance Transactions (Current Month)
  const { data: transactions, error: financeError } = await supabase
    .from('finance_transactions')
    .select('*')
    .gte('date_transaction', startMonth)
    .lte('date_transaction', endMonth)
    .order('date_transaction', { ascending: false });

  if (financeError) {
    console.error('Error fetching finance:', financeError);
  }

  // 2. Fetch Journal Entries (Last 7 Days)
  const { data: journalEntries, error: journalError } = await supabase
    .from('journal_entries')
    .select('*')
    .gte('created_at', sevenDaysAgo)
    .order('created_at', { ascending: true });

  if (journalError) {
    console.error('Error fetching journal:', journalError);
  }

  // 3. Fetch Activities (Latest 5)
  const { data: activities, error: activityError } = await supabase
    .from('activities')
    .select('*')
    .order('created_at', { ascending: false })
    .limit(5);

  if (activityError) {
    console.error('Error fetching activities:', activityError);
  }

  // 4. Transformations

  // Calculate Total Spent
  const totalSpent = transactions?.reduce((sum, t) => sum + Number(t.amount), 0) || 0;

  // Group by Category for Donut Chart
  const expensesByCategory: Record<string, number> = {};
  transactions?.forEach((t) => {
    const category = t.category || 'Uncategorized';
    expensesByCategory[category] = (expensesByCategory[category] || 0) + Number(t.amount);
  });

  const donutChartData = Object.entries(expensesByCategory).map(([name, value]) => ({
    name,
    value,
  }));

  // Map Mood Score for Area Chart
  const moodChartData = journalEntries?.map((entry) => ({
    date: format(new Date(entry.created_at!), 'MMM dd'),
    Mood: entry.mood_score,
  })) || [];

  return {
    transactions: (transactions as Transaction[]) || [],
    journalEntries: (journalEntries as JournalEntry[]) || [],
    activities: (activities as Activity[]) || [],
    totalSpent,
    donutChartData,
    moodChartData,
  };
}
