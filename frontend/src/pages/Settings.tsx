import { useState } from 'react';
import { Bell, Shield, Palette, Database, Save, ChevronRight } from 'lucide-react';
import { useUIStore } from '../stores';

interface SettingsSection {
  id: string;
  title: string;
  icon: any;
  items: SettingsItem[];
}

interface SettingsItem {
  id: string;
  label: string;
  description?: string;
  type: 'toggle' | 'select' | 'input' | 'section';
  value?: any;
  options?: { label: string; value: string }[];
}

function Settings() {
  const { theme, setTheme } = useUIStore();
  const [activeSection, setActiveSection] = useState('notifications');
  const [saving, setSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState('');

  const [settings, setSettings] = useState({
    // Notification Settings
    emailNotifications: true,
    pushNotifications: true,
    maintenanceAlerts: true,
    complianceAlerts: true,
    weeklyDigest: false,

    // Security Settings
    twoFactorEnabled: false,
    sessionTimeout: '30',
    passwordExpiry: '90',

    // Appearance Settings
    language: 'en',
    dateFormat: 'MM/DD/YYYY',
    timezone: 'UTC',

    // Data Settings
    autoSave: true,
    exportFormat: 'csv',
    retentionPeriod: '365',
  });

  const sections: SettingsSection[] = [
    {
      id: 'notifications',
      title: 'Notifications',
      icon: Bell,
      items: [
        { 
          id: 'emailNotifications', 
          label: 'Email Notifications', 
          description: 'Receive email notifications for important updates',
          type: 'toggle', 
          value: settings.emailNotifications 
        },
        { 
          id: 'pushNotifications', 
          label: 'Push Notifications', 
          description: 'Receive push notifications in browser',
          type: 'toggle', 
          value: settings.pushNotifications 
        },
        { 
          id: 'maintenanceAlerts', 
          label: 'Maintenance Alerts', 
          description: 'Get notified about maintenance schedules',
          type: 'toggle', 
          value: settings.maintenanceAlerts 
        },
        { 
          id: 'complianceAlerts', 
          label: 'Compliance Alerts', 
          description: 'Get notified about compliance issues',
          type: 'toggle', 
          value: settings.complianceAlerts 
        },
        { 
          id: 'weeklyDigest', 
          label: 'Weekly Digest', 
          description: 'Receive weekly summary of activities',
          type: 'toggle', 
          value: settings.weeklyDigest 
        },
      ],
    },
    {
      id: 'security',
      title: 'Security',
      icon: Shield,
      items: [
        { 
          id: 'twoFactorEnabled', 
          label: 'Two-Factor Authentication', 
          description: 'Add an extra layer of security',
          type: 'toggle', 
          value: settings.twoFactorEnabled 
        },
        { 
          id: 'sessionTimeout', 
          label: 'Session Timeout (minutes)', 
          type: 'select', 
          value: settings.sessionTimeout,
          options: [
            { label: '15 minutes', value: '15' },
            { label: '30 minutes', value: '30' },
            { label: '1 hour', value: '60' },
            { label: '4 hours', value: '240' },
          ]
        },
        { 
          id: 'passwordExpiry', 
          label: 'Password Expiry (days)', 
          type: 'select', 
          value: settings.passwordExpiry,
          options: [
            { label: '30 days', value: '30' },
            { label: '60 days', value: '60' },
            { label: '90 days', value: '90' },
            { label: 'Never', value: '0' },
          ]
        },
      ],
    },
    {
      id: 'appearance',
      title: 'Appearance',
      icon: Palette,
      items: [
        { 
          id: 'theme', 
          label: 'Theme', 
          type: 'select', 
          value: theme,
          options: [
            { label: 'Light', value: 'light' },
            { label: 'Dark', value: 'dark' },
            { label: 'System', value: 'system' },
          ]
        },
        { 
          id: 'language', 
          label: 'Language', 
          type: 'select', 
          value: settings.language,
          options: [
            { label: 'English', value: 'en' },
            { label: 'Spanish', value: 'es' },
            { label: 'French', value: 'fr' },
            { label: 'German', value: 'de' },
          ]
        },
        { 
          id: 'dateFormat', 
          label: 'Date Format', 
          type: 'select', 
          value: settings.dateFormat,
          options: [
            { label: 'MM/DD/YYYY', value: 'MM/DD/YYYY' },
            { label: 'DD/MM/YYYY', value: 'DD/MM/YYYY' },
            { label: 'YYYY-MM-DD', value: 'YYYY-MM-DD' },
          ]
        },
        { 
          id: 'timezone', 
          label: 'Timezone', 
          type: 'select', 
          value: settings.timezone,
          options: [
            { label: 'UTC', value: 'UTC' },
            { label: 'Eastern Time', value: 'EST' },
            { label: 'Central Time', value: 'CST' },
            { label: 'Pacific Time', value: 'PST' },
          ]
        },
      ],
    },
    {
      id: 'data',
      title: 'Data',
      icon: Database,
      items: [
        { 
          id: 'autoSave', 
          label: 'Auto-Save', 
          description: 'Automatically save changes',
          type: 'toggle', 
          value: settings.autoSave 
        },
        { 
          id: 'exportFormat', 
          label: 'Default Export Format', 
          type: 'select', 
          value: settings.exportFormat,
          options: [
            { label: 'CSV', value: 'csv' },
            { label: 'Excel', value: 'xlsx' },
            { label: 'PDF', value: 'pdf' },
            { label: 'JSON', value: 'json' },
          ]
        },
        { 
          id: 'retentionPeriod', 
          label: 'Data Retention Period (days)', 
          type: 'select', 
          value: settings.retentionPeriod,
          options: [
            { label: '30 days', value: '30' },
            { label: '90 days', value: '90' },
            { label: '180 days', value: '180' },
            { label: '1 year', value: '365' },
            { label: 'Forever', value: '0' },
          ]
        },
      ],
    },
  ];

  const handleSettingChange = (key: string, value: any) => {
    if (key === 'theme') {
      setTheme(value);
    } else {
      setSettings((prev) => ({ ...prev, [key]: value }));
    }
  };

  const handleSave = async () => {
    setSaving(true);
    setSaveMessage('');
    
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1000));
    
    setSaving(false);
    setSaveMessage('Settings saved successfully!');
    
    setTimeout(() => setSaveMessage(''), 3000);
  };

  const renderSettingItem = (item: SettingsItem) => {
    switch (item.type) {
      case 'toggle':
        return (
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-slate-900 dark:text-white">{item.label}</p>
              {item.description && <p className="text-sm text-slate-500 dark:text-slate-400">{item.description}</p>}
            </div>
            <button
              onClick={() => handleSettingChange(item.id, !item.value)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                item.value ? 'bg-blue-600' : 'bg-slate-200 dark:bg-slate-600'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  item.value ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>
        );

      case 'select':
        return (
          <div className="flex items-center justify-between">
            <p className="font-medium text-slate-900 dark:text-white">{item.label}</p>
            <select
              value={item.value}
              onChange={(e) => handleSettingChange(item.id, e.target.value)}
              className="px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-slate-700 text-slate-900 dark:text-white"
            >
              {item.options?.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        );

      case 'input':
        return (
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">{item.label}</label>
            <input
              type="text"
              value={item.value}
              onChange={(e) => handleSettingChange(item.id, e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-slate-700 text-slate-900 dark:text-white"
            />
          </div>
        );

      default:
        return null;
    }
  };

  const activeSectionData = sections.find((s) => s.id === activeSection);

  return (
    <div className="space-y-4 md:space-y-6">
      <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-3">
        <div>
          <h1 className="text-xl md:text-2xl font-bold text-slate-900 dark:text-white">Settings</h1>
          <p className="text-xs md:text-sm text-slate-500 dark:text-slate-400">Manage your account and application preferences</p>
        </div>
        <button
          onClick={handleSave}
          disabled={saving}
          className="flex items-center gap-2 px-4 md:px-6 py-2 md:py-2.5 bg-blue-600 text-white rounded-lg text-xs md:text-sm hover:bg-blue-700 transition-colors disabled:opacity-50 self-start md:self-auto"
        >
          <Save className="h-3.5 w-3.5 md:h-4 md:w-4" />
          {saving ? 'Saving...' : 'Save Changes'}
        </button>
      </div>

      {saveMessage && (
        <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 text-green-700 dark:text-green-400 px-3 md:px-4 py-2 md:py-3 rounded-lg text-xs md:text-sm">
          {saveMessage}
        </div>
      )}

      <div className="flex flex-col md:flex-row gap-4 md:gap-6">
        {/* Sidebar */}
        <div className="w-full md:w-64 flex-shrink-0">
          <nav className="space-y-1">
            {sections.map((section) => {
              const Icon = section.icon;
              return (
                <button
                  key={section.id}
                  onClick={() => setActiveSection(section.id)}
                  className={`w-full flex items-center gap-2 md:gap-3 px-3 md:px-4 py-2 md:py-3 rounded-lg text-left transition-colors ${
                    activeSection === section.id
                      ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-900 dark:text-blue-400 font-medium'
                      : 'text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800'
                  }`}
                >
                  <Icon className="h-4 w-4 md:h-5 md:w-5" />
                  <span className="text-xs md:text-sm">{section.title}</span>
                  <ChevronRight className="h-3 w-3 md:h-4 md:w-4 ml-auto hidden md:block" />
                </button>
              );
            })}
          </nav>
        </div>

        {/* Content */}
        <div className="flex-1">
          {activeSectionData && (
            <div className="bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 p-4 md:p-6">
              <h2 className="text-base md:text-lg font-semibold text-slate-900 dark:text-white mb-4 md:mb-6">{activeSectionData.title}</h2>
              <div className="space-y-4 md:space-y-6">
                {activeSectionData.items.map((item) => (
                  <div key={item.id} className="pb-4 md:pb-6 border-b border-slate-200 dark:border-slate-700 last:border-0 last:pb-0">
                    {renderSettingItem(item)}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Settings;
