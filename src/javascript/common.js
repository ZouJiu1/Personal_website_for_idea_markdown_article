export async function saveFile() {
    try {
      // 创建一个新句柄
    //   const newHandle = await window.showSaveFilePicker();

      const newHandle = currentDirHandle.getDirectoryHandle("/home/zj/article_tmp.md", { create: true });

      // 创建一个 FileSystemWritableFileStream 用于写入
      const writableStream = await newHandle.createWritable();
  
      // 写入我们的文件
      await writableStream.write("This is my file content");
  
      // 关闭文件并将内容写入磁盘
      await writableStream.close();
    } catch (err) {
      console.error(err.name, err.message);
    }
}
export default saveFile