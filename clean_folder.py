
import os
import shutil


class CleanFolder:
    def __init__(self, path, file_types: dict=None):
        if not os.path.exists(path):
            print("지정한 폴더가 존재하지 않습니다.")
            return
    
        self.path = path
        
        if file_types == None:
            # 2. 확장자별로 모을 폴더 이름을 지정합니다.
            file_types = {
                "Sounds": [".mp3", ".wav", ".ogg", ".flac", ".aac", ".m4a"],
                "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tif"],
                "Documents": [".txt", ".pdf", ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt", ".hwp"],
                "Archives": [".zip", ".rar", ".7z", ".tar", ".jar", ".apk"],
                "Programs": [".exe", ".msi"]
            }
        
        self.file_types = file_types


    def clean(self):
        self.execute(self.path)
    
    def execute(self, work_path, depth: int=0):
        # 폴더 내 모든 파일을 확인
        for filename in os.listdir(work_path):
            full_file_path = os.path.join(work_path, filename)
            
            # 파일이면 재귀 호출
            if os.path.isdir(full_file_path):
                if depth < 1:
                    self.execute(full_file_path, depth+1)
    
                continue
                
            # 파일의 확장자를 추출합니다 (.jpg, .txt 등)
            _, extension = os.path.splitext(filename)
            extension = extension.lower()
            
            # 설정한 확장자 그룹을 돌며 파일을 이동시킵니다.
            moved = False
            for folder_name, extensions in file_types.items():
                if extension in extensions:
                    # 이동할 폴더가 없으면 새로 만듭니다.
                    destination_folder = os.path.join(self.path, folder_name)
                    os.makedirs(destination_folder, exist_ok=True)
                    
                    if not folder_name in work_path:
                        # 파일 이동
                        shutil.move(full_file_path, os.path.join(destination_folder, filename))
                        print(f"[이동] {filename} -> {folder_name} 폴더")

                    moved = True
                    break
            
            # 지정되지 않은 기타 확장자 처리
            if not moved and extension:
                etc_folder = os.path.join(self.path, "Others")
                os.makedirs(etc_folder, exist_ok=True)
                shutil.move(full_file_path, os.path.join(etc_folder, filename))
                print(f"[이동] {filename} -> Others 폴더")

        print("\n✨ 폴더 정리가 완료되었습니다!")


# ==================== 실행 및 검증 ====================
if __name__ == "__main__":
    
    # 1. 정리하고 싶은 폴더 경로를 지정합니다. (예: 다운로드 폴더나 바탕화면)
    # 윈도우 사용자는 경로 앞의 r을 그대로 두세요.
    target_path = r"C:\Users\PC\Downloads" 
    
    # 2. 확장자별로 모을 폴더 이름을 지정합니다.
    file_types = {
        "Sources": [".java", ".js", ".py", ".grade", ".json", ".properties", ".c", ".h", ".cpp"],
        "Sounds": [".mp3", ".wav", ".ogg", ".flac", ".aac", ".m4a"],
        "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tif"],
        "Documents": [".txt", ".pdf", ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt", ".hwp"],
        "Archives": [".zip", ".rar", ".7z", ".tar", ".jar", ".apk"],
        "Programs": [".exe", ".msi"]
    }
    
    # 3. 클래스 생성 및 실행
    clean_folder = CleanFolder(path=target_path, file_types=file_types)
    clean_folder.clean()
