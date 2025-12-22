from model_handler import FoodInference
import cv2

def run_test():
    print("--- 正在初始化模型 ---")
    # 這裡路徑要對應你待會下載存放的位置
    try:
        infer = FoodInference(model_path='models/best.pt', data_path='food_data.json')
        
        # 測試圖片路徑
        test_img = 'test_input.jpg' 
        
        print(f"--- 正在辨識圖片: {test_img} ---")
        result = infer.analyze(test_img)
        
        if result["success"]:
            print("\n✅ 辨識成功！")
            print(f"食物名稱: {result['name']}")
            print(f"熱量預估: {result['calories']} kcal")
            print(f"信心指數: {result['conf']}")
            print(f"營養組成: {result['nutrition']}")
        else:
            print("\n❌ 辨識失敗：模型無法從這張圖片認出支援的食物。")
            
    except Exception as e:
        print(f"\n☢️ 發生錯誤: {e}")

if __name__ == "__main__":
    run_test()