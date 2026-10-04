/**
 * IndexedDB 工具类
 * 完全替代 localStorage，用于存储所有应用数据
 */

const DB_NAME = 'EmotionRecognitionDB'
// 必须保持 2：老用户浏览器中数据库已是 v2，用更低版本打开会抛 VersionError
const DB_VERSION = 2

// 对象存储名称
const STORES = {
  VIDEO_HISTORY: 'video_history',
  IMAGE_PREDICTIONS: 'image_predictions',
  VIDEO_ANALYSIS: 'video_analysis',
}

class IndexedDBHelper {
  constructor() {
    this.db = null
  }

  /**
   * 初始化数据库
   */
  async init() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, DB_VERSION)

      request.onerror = () => {
        console.error('❌ IndexedDB 打开失败:', request.error)
        reject(request.error)
      }

      request.onsuccess = () => {
        this.db = request.result
        console.log('✅ IndexedDB 已连接')
        resolve(this.db)
      }

      request.onupgradeneeded = (event) => {
        const db = event.target.result
        const oldVersion = event.oldVersion
        console.log(`🔄 IndexedDB 升级中... (v${oldVersion} → v${DB_VERSION})`)

        // 创建视频历史对象存储（按用户隔离）
        if (!db.objectStoreNames.contains(STORES.VIDEO_HISTORY)) {
          const videoStore = db.createObjectStore(STORES.VIDEO_HISTORY, { 
            keyPath: 'id', 
            autoIncrement: true 
          })
          videoStore.createIndex('username', 'username', { unique: false })
          videoStore.createIndex('video_id', 'video_id', { unique: false })
          videoStore.createIndex('timestamp', 'timestamp', { unique: false })
          console.log('✅ 创建 video_history 存储')
        }

        // 创建图片预测对象存储
        if (!db.objectStoreNames.contains(STORES.IMAGE_PREDICTIONS)) {
          const imageStore = db.createObjectStore(STORES.IMAGE_PREDICTIONS, { 
            keyPath: 'id', 
            autoIncrement: true 
          })
          imageStore.createIndex('username', 'username', { unique: false })
          imageStore.createIndex('timestamp', 'timestamp', { unique: false })
          console.log('✅ 创建 image_predictions 存储')
        }

        // 创建当前视频分析对象存储
        if (!db.objectStoreNames.contains(STORES.VIDEO_ANALYSIS)) {
          const analysisStore = db.createObjectStore(STORES.VIDEO_ANALYSIS, {
            keyPath: 'username'
          })
          console.log('✅ 创建 video_analysis 存储')
        }
      }
    })
  }

  /**
   * 确保数据库已连接
   */
  async ensureConnection() {
    if (!this.db) {
      await this.init()
    }
  }

  /**
   * 添加数据
   */
  async add(storeName, data) {
    await this.ensureConnection()
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readwrite')
      const store = transaction.objectStore(storeName)
      const request = store.add(data)

      request.onsuccess = () => {
        resolve(request.result)
      }
      request.onerror = () => {
        console.error(`❌ 添加数据失败 [${storeName}]:`, request.error)
        reject(request.error)
      }
    })
  }

  /**
   * 更新数据（如果存在则更新，否则添加）
   */
  async put(storeName, data) {
    await this.ensureConnection()
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readwrite')
      const store = transaction.objectStore(storeName)
      const request = store.put(data)

      request.onsuccess = () => {
        resolve(request.result)
      }
      request.onerror = () => {
        console.error(`❌ 更新数据失败 [${storeName}]:`, request.error)
        reject(request.error)
      }
    })
  }

  /**
   * 根据 key 获取数据
   */
  async get(storeName, key) {
    await this.ensureConnection()
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readonly')
      const store = transaction.objectStore(storeName)
      const request = store.get(key)

      request.onsuccess = () => {
        resolve(request.result)
      }
      request.onerror = () => {
        reject(request.error)
      }
    })
  }

  /**
   * 根据索引查询数据
   */
  async getByIndex(storeName, indexName, value) {
    await this.ensureConnection()
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readonly')
      const store = transaction.objectStore(storeName)
      const index = store.index(indexName)
      const request = index.getAll(value)

      request.onsuccess = () => {
        resolve(request.result)
      }
      request.onerror = () => {
        reject(request.error)
      }
    })
  }

  /**
   * 获取所有数据
   */
  async getAll(storeName) {
    await this.ensureConnection()
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readonly')
      const store = transaction.objectStore(storeName)
      const request = store.getAll()

      request.onsuccess = () => {
        resolve(request.result)
      }
      request.onerror = () => {
        reject(request.error)
      }
    })
  }

  /**
   * 删除数据
   */
  async delete(storeName, key) {
    await this.ensureConnection()
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readwrite')
      const store = transaction.objectStore(storeName)
      const request = store.delete(key)

      request.onsuccess = () => {
        resolve()
      }
      request.onerror = () => {
        reject(request.error)
      }
    })
  }

  /**
   * 清空对象存储
   */
  async clear(storeName) {
    await this.ensureConnection()
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readwrite')
      const store = transaction.objectStore(storeName)
      const request = store.clear()

      request.onsuccess = () => {
        resolve()
      }
      request.onerror = () => {
        reject(request.error)
      }
    })
  }

  /**
   * 根据索引删除多条数据
   */
  async deleteByIndex(storeName, indexName, value) {
    await this.ensureConnection()
    const items = await this.getByIndex(storeName, indexName, value)
    const promises = items.map(item => this.delete(storeName, item.id))
    return Promise.all(promises)
  }

  /**
   * 统计数据条数
   */
  async count(storeName) {
    await this.ensureConnection()
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readonly')
      const store = transaction.objectStore(storeName)
      const request = store.count()

      request.onsuccess = () => {
        resolve(request.result)
      }
      request.onerror = () => {
        reject(request.error)
      }
    })
  }
}

// 导出单例
const dbHelper = new IndexedDBHelper()

export default dbHelper
export { STORES }
