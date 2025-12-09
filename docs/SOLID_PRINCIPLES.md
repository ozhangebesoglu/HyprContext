# 🏗️ HyprContext SOLID Prensipleri

Bu dokümanda, HyprContext projesinde kullanılacak SOLID prensipleri ve uygulama örnekleri yer almaktadır.

---

## 📋 SOLID Nedir?

| Harf | İlke | Açıklama |
|------|------|----------|
| **S** | Single Responsibility | Her sınıf/modül tek bir iş yapmalı |
| **O** | Open/Closed | Genişlemeye açık, değişikliğe kapalı |
| **L** | Liskov Substitution | Alt sınıflar, üst sınıfların yerine geçebilmeli |
| **I** | Interface Segregation | Küçük, özelleşmiş arayüzler kullan |
| **D** | Dependency Inversion | Soyutlamalara bağımlı ol, somut uygulamalara değil |

---

## 1️⃣ Single Responsibility Principle (SRP)

### ❌ Yanlış - Backend
```python
# Tek bir sınıf her şeyi yapıyor
class ActivityService:
    def capture_screenshot(self):
        # Screenshot al
        pass
    
    def get_window_info(self):
        # Pencere bilgisi al
        pass
    
    def analyze_with_ai(self, screenshot, window_info):
        # AI analizi yap
        pass
    
    def save_to_database(self, analysis):
        # Veritabanına kaydet
        pass
    
    def send_notification(self, message):
        # Bildirim gönder
        pass
    
    def generate_report(self):
        # Rapor oluştur
        pass
```

### ✅ Doğru - Backend
```python
# Her sınıf tek bir sorumluluk

class ScreenshotService:
    """Sadece ekran görüntüsü alma işlemi"""
    def capture(self) -> bytes:
        pass

class WindowService:
    """Sadece pencere bilgisi alma işlemi"""
    def get_active_window(self) -> WindowInfo:
        pass
    
    def get_all_windows(self) -> list[WindowInfo]:
        pass

class AIAnalyzer:
    """Sadece AI analizi işlemi"""
    def analyze(self, screenshot: bytes, windows: list[WindowInfo]) -> Analysis:
        pass

class ActivityRepository:
    """Sadece veritabanı işlemleri"""
    def save(self, activity: Activity) -> bool:
        pass
    
    def get_by_date(self, date: str) -> list[Activity]:
        pass

class NotificationService:
    """Sadece bildirim işlemleri"""
    def send(self, title: str, message: str) -> None:
        pass

class ReportGenerator:
    """Sadece rapor oluşturma işlemi"""
    def generate(self, activities: list[Activity]) -> Report:
        pass
```

### ❌ Yanlış - Frontend
```tsx
// Tek bir component her şeyi yapıyor
const Dashboard = () => {
  const [activities, setActivities] = useState([]);
  const [isRunning, setIsRunning] = useState(false);
  const [stats, setStats] = useState(null);
  
  // API çağrıları
  const fetchActivities = async () => { /* ... */ };
  const startCapture = async () => { /* ... */ };
  const stopCapture = async () => { /* ... */ };
  
  // Render logic
  const renderActivityCard = (activity) => { /* ... */ };
  const renderStats = () => { /* ... */ };
  const renderControls = () => { /* ... */ };
  
  // Event handlers
  const handleStart = () => { /* ... */ };
  const handleStop = () => { /* ... */ };
  
  return (
    <div>
      {/* 200+ satır JSX */}
    </div>
  );
};
```

### ✅ Doğru - Frontend
```tsx
// Her component tek bir sorumluluk

// hooks/useActivities.ts - Sadece aktivite verisi
export const useActivities = () => {
  const [activities, setActivities] = useState<Activity[]>([]);
  const fetchActivities = async () => { /* ... */ };
  return { activities, fetchActivities };
};

// hooks/useCaptureControl.ts - Sadece capture kontrolü
export const useCaptureControl = () => {
  const [isRunning, setIsRunning] = useState(false);
  const start = async () => { /* ... */ };
  const stop = async () => { /* ... */ };
  return { isRunning, start, stop };
};

// components/ActivityCard.tsx - Sadece aktivite kartı gösterimi
export const ActivityCard = ({ activity }: { activity: Activity }) => {
  return (
    <GlassCard>
      <time>{activity.timestamp}</time>
      <p>{activity.summary}</p>
      <TagList tags={activity.tags} />
    </GlassCard>
  );
};

// components/CaptureControls.tsx - Sadece kontrol butonları
export const CaptureControls = ({ isRunning, onStart, onStop }) => {
  return (
    <div>
      <GlassButton onClick={isRunning ? onStop : onStart}>
        {isRunning ? '⏸️ Durdur' : '▶️ Başlat'}
      </GlassButton>
    </div>
  );
};

// components/StatsCard.tsx - Sadece istatistik gösterimi
export const StatsCard = ({ stats }: { stats: Stats }) => {
  return (
    <GlassCard>
      <StatItem label="Kayıt" value={stats.count} />
      <StatItem label="Süre" value={stats.duration} />
    </GlassCard>
  );
};

// pages/Dashboard.tsx - Sadece composition
export const Dashboard = () => {
  const { activities, fetchActivities } = useActivities();
  const { isRunning, start, stop } = useCaptureControl();
  const { stats } = useStats();
  
  return (
    <PageContainer>
      <CaptureControls isRunning={isRunning} onStart={start} onStop={stop} />
      <StatsCard stats={stats} />
      <ActivityList activities={activities} />
    </PageContainer>
  );
};
```

---

## 2️⃣ Open/Closed Principle (OCP)

### ❌ Yanlış - Backend
```python
# Yeni AI modeli eklemek için mevcut kodu değiştirmek gerekiyor
class AIAnalyzer:
    def analyze(self, screenshot: bytes, model: str) -> str:
        if model == "gemma3":
            return self._analyze_with_gemma(screenshot)
        elif model == "llama":
            return self._analyze_with_llama(screenshot)
        elif model == "gpt4":
            return self._analyze_with_gpt4(screenshot)
        # Yeni model eklemek için buraya yeni elif eklemek gerekiyor!
        else:
            raise ValueError(f"Unknown model: {model}")
    
    def _analyze_with_gemma(self, screenshot):
        # Gemma implementasyonu
        pass
    
    def _analyze_with_llama(self, screenshot):
        # Llama implementasyonu
        pass
```

### ✅ Doğru - Backend
```python
# Soyutlama ile genişlemeye açık, değişikliğe kapalı
from abc import ABC, abstractmethod

class AIModelBase(ABC):
    """Tüm AI modelleri için soyut temel sınıf"""
    
    @abstractmethod
    def analyze(self, screenshot: bytes, prompt: str) -> str:
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        pass

class GemmaModel(AIModelBase):
    def analyze(self, screenshot: bytes, prompt: str) -> str:
        # Gemma implementasyonu
        response = ollama.generate(model="gemma3", prompt=prompt, images=[screenshot])
        return response["response"]
    
    def get_name(self) -> str:
        return "gemma3"

class LlamaModel(AIModelBase):
    def analyze(self, screenshot: bytes, prompt: str) -> str:
        # Llama implementasyonu
        response = ollama.generate(model="llama", prompt=prompt, images=[screenshot])
        return response["response"]
    
    def get_name(self) -> str:
        return "llama"

# Yeni model eklemek için sadece yeni sınıf oluştur - mevcut kodu değiştirme!
class GPT4Model(AIModelBase):
    def analyze(self, screenshot: bytes, prompt: str) -> str:
        # GPT-4 implementasyonu
        pass
    
    def get_name(self) -> str:
        return "gpt-4"

# Analyzer sınıfı modelden bağımsız
class AIAnalyzer:
    def __init__(self, model: AIModelBase):
        self.model = model
    
    def analyze(self, screenshot: bytes, prompt: str) -> str:
        return self.model.analyze(screenshot, prompt)

# Kullanım
analyzer = AIAnalyzer(GemmaModel())
result = analyzer.analyze(screenshot, prompt)

# Yeni model eklemek kolay
analyzer = AIAnalyzer(GPT4Model())
```

### ❌ Yanlış - Frontend
```tsx
// Yeni glass variant eklemek için switch'i değiştirmek gerekiyor
const GlassCard = ({ variant }: { variant: string }) => {
  let styles = {};
  
  switch (variant) {
    case 'solid':
      styles = { blur: '20px', opacity: 0.5 };
      break;
    case 'light':
      styles = { blur: '10px', opacity: 0.3 };
      break;
    // Yeni variant için buraya case eklemek gerekiyor!
    default:
      styles = { blur: '20px', opacity: 0.5 };
  }
  
  return <div style={styles}>{/* ... */}</div>;
};
```

### ✅ Doğru - Frontend
```tsx
// Variant'lar config olarak tanımlanıyor
const GLASS_VARIANTS = {
  solid: { blur: '20px', tint: 'rgba(255,255,255,0.5)' },
  light: { blur: '10px', tint: 'rgba(255,255,255,0.3)' },
  heavy: { blur: '30px', tint: 'rgba(255,255,255,0.6)' },
  subtle: { blur: '5px', tint: 'rgba(255,255,255,0.2)' },
} as const;

type GlassVariant = keyof typeof GLASS_VARIANTS;

// Yeni variant eklemek için sadece config'e ekle!
// Component koduna dokunmaya gerek yok

interface GlassCardProps {
  variant?: GlassVariant;
  children: React.ReactNode;
}

const GlassCard = ({ variant = 'solid', children }: GlassCardProps) => {
  const config = GLASS_VARIANTS[variant];
  
  return (
    <div 
      style={{ 
        backdropFilter: `blur(${config.blur})`,
        background: config.tint 
      }}
    >
      {children}
    </div>
  );
};
```

---

## 3️⃣ Liskov Substitution Principle (LSP)

### ❌ Yanlış - Backend
```python
class BaseNotification:
    def send(self, message: str) -> bool:
        raise NotImplementedError

class DesktopNotification(BaseNotification):
    def send(self, message: str) -> bool:
        # notify-send kullan
        subprocess.run(["notify-send", message])
        return True

class EmailNotification(BaseNotification):
    def send(self, message: str, recipient: str) -> bool:  # ❌ Farklı imza!
        # Email gönder
        pass

# Bu çalışmaz çünkü EmailNotification farklı parametre bekliyor
def notify_user(notification: BaseNotification, message: str):
    notification.send(message)  # ❌ EmailNotification için hata!
```

### ✅ Doğru - Backend
```python
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class NotificationMessage:
    title: str
    body: str
    recipient: str = None  # Opsiyonel

class BaseNotification(ABC):
    @abstractmethod
    def send(self, message: NotificationMessage) -> bool:
        pass

class DesktopNotification(BaseNotification):
    def send(self, message: NotificationMessage) -> bool:
        subprocess.run(["notify-send", message.title, message.body])
        return True

class EmailNotification(BaseNotification):
    def send(self, message: NotificationMessage) -> bool:
        if not message.recipient:
            return False
        # Email gönder
        return True

class TTSNotification(BaseNotification):
    def send(self, message: NotificationMessage) -> bool:
        # Sesli uyarı
        subprocess.run(["edge-tts", "--text", message.body])
        return True

# Artık hepsi aynı şekilde kullanılabilir
def notify_user(notification: BaseNotification, message: NotificationMessage):
    notification.send(message)  # ✅ Tüm alt sınıflar için çalışır

# Kullanım
desktop = DesktopNotification()
email = EmailNotification()
tts = TTSNotification()

msg = NotificationMessage(title="Uyarı", body="Dikkat dağınıklığı!", recipient="user@email.com")

notify_user(desktop, msg)  # ✅ Çalışır
notify_user(email, msg)    # ✅ Çalışır
notify_user(tts, msg)      # ✅ Çalışır
```

### ❌ Yanlış - Frontend
```tsx
interface ButtonProps {
  onClick: () => void;
  children: React.ReactNode;
}

const GlassButton = ({ onClick, children }: ButtonProps) => {
  return <button onClick={onClick}>{children}</button>;
};

// Link butonu farklı davranıyor - onClick yerine href bekliyor
const GlassLinkButton = ({ href, children }) => {  // ❌ Farklı props!
  return <a href={href}>{children}</a>;
};

// Bu component'i buton yerine kullanamayız
const ActionBar = ({ onAction }: { onAction: () => void }) => {
  return <GlassButton onClick={onAction}>Click</GlassButton>;
  // GlassLinkButton burada çalışmaz!
};
```

### ✅ Doğru - Frontend
```tsx
// Ortak interface
interface ActionableProps {
  children: React.ReactNode;
  className?: string;
}

interface ClickableProps extends ActionableProps {
  type: 'button';
  onClick: () => void;
}

interface LinkableProps extends ActionableProps {
  type: 'link';
  href: string;
}

type GlassButtonProps = ClickableProps | LinkableProps;

const GlassButton = (props: GlassButtonProps) => {
  const baseClass = "glass glass-light px-4 py-2";
  
  if (props.type === 'link') {
    return (
      <a href={props.href} className={baseClass}>
        {props.children}
      </a>
    );
  }
  
  return (
    <button onClick={props.onClick} className={baseClass}>
      {props.children}
    </button>
  );
};

// Her iki türde de çalışır
<GlassButton type="button" onClick={() => console.log('clicked')}>
  Click Me
</GlassButton>

<GlassButton type="link" href="/dashboard">
  Go to Dashboard
</GlassButton>
```

---

## 4️⃣ Interface Segregation Principle (ISP)

### ❌ Yanlış - Backend
```python
# Büyük, monolitik interface
class IActivityService(ABC):
    @abstractmethod
    def capture_screenshot(self) -> bytes:
        pass
    
    @abstractmethod
    def analyze_activity(self, screenshot: bytes) -> str:
        pass
    
    @abstractmethod
    def save_activity(self, activity: Activity) -> bool:
        pass
    
    @abstractmethod
    def generate_report(self) -> Report:
        pass
    
    @abstractmethod
    def generate_plan(self) -> Plan:
        pass
    
    @abstractmethod
    def send_notification(self, message: str) -> None:
        pass
    
    @abstractmethod
    def track_focus(self) -> FocusData:
        pass

# Bu sınıf sadece rapor oluşturuyor ama diğer tüm metodları da
# implement etmek zorunda!
class ReportService(IActivityService):
    def capture_screenshot(self) -> bytes:
        raise NotImplementedError  # ❌ Kullanılmıyor ama implement etmek zorunda
    
    def analyze_activity(self, screenshot: bytes) -> str:
        raise NotImplementedError  # ❌ Kullanılmıyor
    
    # ... diğer kullanılmayan metodlar ...
    
    def generate_report(self) -> Report:
        # Sadece bu kullanılıyor
        pass
```

### ✅ Doğru - Backend
```python
# Küçük, odaklı interface'ler

class IScreenshotCapture(ABC):
    @abstractmethod
    def capture(self) -> bytes:
        pass

class IActivityAnalyzer(ABC):
    @abstractmethod
    def analyze(self, screenshot: bytes) -> Analysis:
        pass

class IActivityRepository(ABC):
    @abstractmethod
    def save(self, activity: Activity) -> bool:
        pass
    
    @abstractmethod
    def get_by_date(self, date: str) -> list[Activity]:
        pass

class IReportGenerator(ABC):
    @abstractmethod
    def generate(self, activities: list[Activity]) -> Report:
        pass

class IPlanGenerator(ABC):
    @abstractmethod
    def generate(self, context: PlanContext) -> Plan:
        pass

class INotificationSender(ABC):
    @abstractmethod
    def send(self, message: NotificationMessage) -> bool:
        pass

class IFocusTracker(ABC):
    @abstractmethod
    def check_distraction(self) -> tuple[bool, str | None]:
        pass
    
    @abstractmethod
    def get_today_stats(self) -> FocusStats:
        pass

# Şimdi her sınıf sadece ihtiyacı olan interface'i implement eder

class ReportService(IReportGenerator):
    def __init__(self, repository: IActivityRepository):
        self.repository = repository
    
    def generate(self, activities: list[Activity]) -> Report:
        # Sadece rapor oluşturma sorumluluğu
        pass

class CaptureService(IScreenshotCapture, IActivityAnalyzer):
    # Birden fazla küçük interface implement edebilir
    def capture(self) -> bytes:
        pass
    
    def analyze(self, screenshot: bytes) -> Analysis:
        pass
```

### ❌ Yanlış - Frontend
```tsx
// Büyük, her şeyi içeren props
interface ActivityComponentProps {
  activity: Activity;
  onEdit: (id: string) => void;
  onDelete: (id: string) => void;
  onShare: (id: string) => void;
  onExport: (id: string) => void;
  onAddTag: (id: string, tag: string) => void;
  onRemoveTag: (id: string, tag: string) => void;
  showActions: boolean;
  showTags: boolean;
  showTimestamp: boolean;
  isEditable: boolean;
  isSelectable: boolean;
  isSelected: boolean;
  onSelect: (id: string) => void;
}

// Component kullanımı zorlaşıyor
<ActivityCard 
  activity={activity}
  onEdit={() => {}}      // Kullanmıyorum ama vermek zorundayım
  onDelete={() => {}}    // Kullanmıyorum ama vermek zorundayım
  onShare={() => {}}     // Kullanmıyorum ama vermek zorundayım
  onExport={() => {}}    // Kullanmıyorum ama vermek zorundayım
  // ... 10+ prop daha
/>
```

### ✅ Doğru - Frontend
```tsx
// Küçük, odaklı interface'ler

// Temel aktivite gösterimi
interface ActivityDisplayProps {
  activity: Activity;
  showTimestamp?: boolean;
}

// Etiket işlemleri
interface TaggableProps {
  tags: string[];
  onAddTag?: (tag: string) => void;
  onRemoveTag?: (tag: string) => void;
}

// Seçilebilir
interface SelectableProps {
  isSelected: boolean;
  onSelect: () => void;
}

// Düzenlenebilir
interface EditableProps {
  onEdit: () => void;
  onDelete: () => void;
}

// Basit gösterim için
const ActivityCard = ({ activity, showTimestamp = true }: ActivityDisplayProps) => {
  return (
    <GlassCard>
      {showTimestamp && <time>{activity.timestamp}</time>}
      <p>{activity.summary}</p>
    </GlassCard>
  );
};

// Etiketli gösterim için
const TaggableActivityCard = ({ 
  activity, 
  tags, 
  onAddTag, 
  onRemoveTag 
}: ActivityDisplayProps & TaggableProps) => {
  return (
    <GlassCard>
      <p>{activity.summary}</p>
      <TagList tags={tags} onAdd={onAddTag} onRemove={onRemoveTag} />
    </GlassCard>
  );
};

// Seçilebilir gösterim için
const SelectableActivityCard = ({
  activity,
  isSelected,
  onSelect
}: ActivityDisplayProps & SelectableProps) => {
  return (
    <GlassCard className={isSelected ? 'selected' : ''} onClick={onSelect}>
      <p>{activity.summary}</p>
    </GlassCard>
  );
};

// Composition ile birleştir - sadece ihtiyacın olanı kullan
const FullFeaturedActivityCard = ({
  activity,
  tags,
  isSelected,
  onSelect,
  onEdit
}: ActivityDisplayProps & TaggableProps & SelectableProps & Pick<EditableProps, 'onEdit'>) => {
  return (
    <SelectableActivityCard activity={activity} isSelected={isSelected} onSelect={onSelect}>
      <TagList tags={tags} />
      <button onClick={onEdit}>Düzenle</button>
    </SelectableActivityCard>
  );
};
```

---

## 5️⃣ Dependency Inversion Principle (DIP)

### ❌ Yanlış - Backend
```python
# Üst seviye modül (CaptureService) alt seviye modüle (OllamaClient) doğrudan bağımlı
class OllamaClient:
    def generate(self, prompt: str, image: bytes) -> str:
        response = requests.post("http://localhost:11434/api/generate", ...)
        return response.json()["response"]

class CaptureService:
    def __init__(self):
        self.ai_client = OllamaClient()  # ❌ Doğrudan bağımlılık
        self.db = ChromaDBClient()       # ❌ Doğrudan bağımlılık
    
    def capture_and_analyze(self):
        screenshot = self._capture()
        analysis = self.ai_client.generate("Analyze this", screenshot)  # ❌
        self.db.save(analysis)  # ❌
        return analysis
```

### ✅ Doğru - Backend
```python
# Soyutlamalar (Interface'ler)
class IAIClient(ABC):
    @abstractmethod
    def generate(self, prompt: str, image: bytes) -> str:
        pass

class IDatabase(ABC):
    @abstractmethod
    def save(self, data: dict) -> bool:
        pass
    
    @abstractmethod
    def query(self, query: str) -> list:
        pass

# Somut implementasyonlar
class OllamaClient(IAIClient):
    def generate(self, prompt: str, image: bytes) -> str:
        response = requests.post("http://localhost:11434/api/generate", ...)
        return response.json()["response"]

class OpenAIClient(IAIClient):
    def generate(self, prompt: str, image: bytes) -> str:
        # OpenAI API kullan
        pass

class ChromaDBClient(IDatabase):
    def save(self, data: dict) -> bool:
        # ChromaDB'ye kaydet
        pass
    
    def query(self, query: str) -> list:
        pass

class SQLiteClient(IDatabase):
    def save(self, data: dict) -> bool:
        # SQLite'a kaydet
        pass
    
    def query(self, query: str) -> list:
        pass

# Üst seviye modül soyutlamalara bağımlı
class CaptureService:
    def __init__(self, ai_client: IAIClient, database: IDatabase):  # ✅ Soyutlama
        self.ai_client = ai_client
        self.database = database
    
    def capture_and_analyze(self):
        screenshot = self._capture()
        analysis = self.ai_client.generate("Analyze this", screenshot)
        self.database.save({"analysis": analysis})
        return analysis

# Dependency Injection ile kullanım
ollama = OllamaClient()
chromadb = ChromaDBClient()
service = CaptureService(ai_client=ollama, database=chromadb)

# Kolayca değiştirilebilir
openai = OpenAIClient()
sqlite = SQLiteClient()
service = CaptureService(ai_client=openai, database=sqlite)
```

### ❌ Yanlış - Frontend
```tsx
// Component doğrudan API'ye bağımlı
const ActivityList = () => {
  const [activities, setActivities] = useState([]);
  
  useEffect(() => {
    // ❌ Doğrudan fetch - test edilemez, değiştirilemez
    fetch('http://localhost:8000/activities')
      .then(res => res.json())
      .then(data => setActivities(data));
  }, []);
  
  return (
    <div>
      {activities.map(a => <ActivityCard key={a.id} activity={a} />)}
    </div>
  );
};
```

### ✅ Doğru - Frontend
```tsx
// 1. API servisi soyutlaması
interface IActivityService {
  getActivities(): Promise<Activity[]>;
  getActivityById(id: string): Promise<Activity>;
  saveActivity(activity: Activity): Promise<void>;
}

// 2. Somut implementasyon
class ActivityApiService implements IActivityService {
  private baseUrl: string;
  
  constructor(baseUrl: string = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }
  
  async getActivities(): Promise<Activity[]> {
    const response = await fetch(`${this.baseUrl}/activities`);
    return response.json();
  }
  
  async getActivityById(id: string): Promise<Activity> {
    const response = await fetch(`${this.baseUrl}/activities/${id}`);
    return response.json();
  }
  
  async saveActivity(activity: Activity): Promise<void> {
    await fetch(`${this.baseUrl}/activities`, {
      method: 'POST',
      body: JSON.stringify(activity),
    });
  }
}

// 3. Mock implementasyon (test için)
class MockActivityService implements IActivityService {
  private activities: Activity[] = [];
  
  async getActivities(): Promise<Activity[]> {
    return this.activities;
  }
  
  async getActivityById(id: string): Promise<Activity> {
    return this.activities.find(a => a.id === id)!;
  }
  
  async saveActivity(activity: Activity): Promise<void> {
    this.activities.push(activity);
  }
}

// 4. Context ile dependency injection
const ActivityServiceContext = createContext<IActivityService | null>(null);

export const ActivityServiceProvider = ({ 
  service, 
  children 
}: { 
  service: IActivityService; 
  children: React.ReactNode 
}) => {
  return (
    <ActivityServiceContext.Provider value={service}>
      {children}
    </ActivityServiceContext.Provider>
  );
};

export const useActivityService = () => {
  const service = useContext(ActivityServiceContext);
  if (!service) throw new Error('ActivityServiceProvider not found');
  return service;
};

// 5. Custom hook - servise bağımlı
export const useActivities = () => {
  const service = useActivityService();
  const [activities, setActivities] = useState<Activity[]>([]);
  
  useEffect(() => {
    service.getActivities().then(setActivities);
  }, [service]);
  
  return { activities };
};

// 6. Component - soyutlamaya bağımlı
const ActivityList = () => {
  const { activities } = useActivities();  // ✅ Soyutlama kullanıyor
  
  return (
    <div>
      {activities.map(a => <ActivityCard key={a.id} activity={a} />)}
    </div>
  );
};

// 7. Kullanım
// Production
const apiService = new ActivityApiService();
<ActivityServiceProvider service={apiService}>
  <App />
</ActivityServiceProvider>

// Test
const mockService = new MockActivityService();
<ActivityServiceProvider service={mockService}>
  <App />
</ActivityServiceProvider>
```

---

## 📁 SOLID Uyumlu Dosya Yapısı

### Backend
```
backend/
├── interfaces/                    # Soyutlamalar (DIP)
│   ├── __init__.py
│   ├── ai_client.py              # IAIClient
│   ├── database.py               # IDatabase
│   ├── notification.py           # INotification
│   └── capture.py                # ICapture
│
├── services/                      # Tek sorumluluk (SRP)
│   ├── screenshot_service.py     # Sadece screenshot
│   ├── window_service.py         # Sadece pencere bilgisi
│   ├── ai_analyzer.py            # Sadece AI analizi
│   ├── focus_tracker.py          # Sadece odak takibi
│   ├── report_generator.py       # Sadece rapor
│   └── plan_generator.py         # Sadece plan
│
├── repositories/                  # Veri erişim (SRP)
│   ├── activity_repository.py
│   ├── plan_repository.py
│   └── report_repository.py
│
├── models/                        # Veri modelleri
│   ├── activity.py
│   ├── plan.py
│   └── report.py
│
├── adapters/                      # Somut implementasyonlar (OCP)
│   ├── ollama_adapter.py         # OllamaClient
│   ├── chromadb_adapter.py       # ChromaDBClient
│   └── notification_adapter.py   # DesktopNotification, TTS
│
└── api/                           # FastAPI routes
    └── routes/
```

### Frontend
```
src/
├── interfaces/                    # TypeScript interfaces
│   ├── services.ts               # IActivityService, etc.
│   └── models.ts                 # Activity, Plan, Report
│
├── services/                      # API servisleri (DIP)
│   ├── ActivityService.ts
│   ├── PlanService.ts
│   └── ReportService.ts
│
├── hooks/                         # Custom hooks (SRP)
│   ├── useActivities.ts
│   ├── useCaptureControl.ts
│   ├── useFocusStats.ts
│   └── useSettings.ts
│
├── components/
│   ├── glass/                    # Glass primitives (ISP)
│   │   ├── GlassCard.tsx
│   │   ├── GlassButton.tsx
│   │   └── ...
│   │
│   ├── features/                 # Feature components (SRP)
│   │   ├── ActivityCard.tsx
│   │   ├── PlanEditor.tsx
│   │   └── ...
│   │
│   └── layout/                   # Layout components (SRP)
│       ├── Dock.tsx
│       └── Sidebar.tsx
│
├── contexts/                      # Dependency injection
│   └── ServiceProvider.tsx
│
└── pages/                         # Page composition
    ├── Home.tsx
    └── ...
```

---

## 🎯 Özet Kontrol Listesi

### Her Sınıf/Component İçin

- [ ] **SRP:** Bu sınıf sadece bir iş mi yapıyor?
- [ ] **OCP:** Yeni özellik eklemek için mevcut kodu değiştirmek gerekiyor mu?
- [ ] **LSP:** Alt sınıflar, üst sınıfların yerine geçebilir mi?
- [ ] **ISP:** Kullanılmayan metodlar/props var mı?
- [ ] **DIP:** Somut sınıflara mı yoksa soyutlamalara mı bağımlı?

---

*Son güncelleme: 2025-12-09*
