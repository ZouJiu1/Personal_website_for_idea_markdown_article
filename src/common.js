import axios from 'axios'
import Cookies from 'js-cookie'

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
export function create_cookie(mail, passw, expires) {
  let meg = "";
  try {
    meg = encodeURIComponent("expires") + "=" + encodeURIComponent(expires) + ";" +
          encodeURIComponent("mail") + "=" + encodeURIComponent(mail) + ";" +
          encodeURIComponent("password") + "=" + encodeURIComponent(passw);
  } catch (err) {
    console.error(err.name, err.message);
  }
  return meg;
}

async function getusername(url) {
  let mail = "";
  let password = "";
  mail = Cookies.get("mail");
  password = Cookies.get("password");
  // console.log('password: ', password, mail, Cookies.get("username"));
  const instance = axios.create({
    baseURL: 'http://localhost:7009/csdn/getusername',
    timeout: 20000,
  });
  
  // console.log(this.search_param);
  let sendret;
  if(!mail) {
    mail = "";
  }
  if(!password) {
    password = "";
  }
  await instance({
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest'
    },
    data: {'url' : url, 'mail': mail, 'password':password},
  }).then((response) => {
    sendret = response.data;
  });
  return sendret;
}

export default getusername