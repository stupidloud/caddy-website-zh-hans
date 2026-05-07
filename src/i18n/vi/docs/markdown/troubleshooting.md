---
title: Chiến lược khắc phục sự cố (Troubleshooting Strategies)
---

Chiến lược khắc phục sự cố
=====================

Trang này trình bày một khung làm việc chung, có phương pháp để bạn tự khắc phục hầu hết các loại vấn đề có thể gặp phải khi sử dụng Caddy _mà không cần sử dụng AI_. Chúng tôi khuyên bạn nên thực hiện các bước tương tự khi yêu cầu trợ giúp trên diễn đàn của chúng tôi. Trong nhiều trường hợp, bạn có thể tự trả lời câu hỏi của mình hoặc khắc phục các vấn đề của chính mình bằng cách áp dụng một số tư duy phản biện.


Bạn biết những gì?
-----------------

Có thể bạn không biết vấn đề là gì, nguyên nhân gây ra nó hoặc cách khắc phục, vì vậy hãy bắt đầu với một số điều cơ bản mà chắc chắn bạn biết:

<a id="what-you-expect"></a>
### Những gì bạn mong đợi

Hãy nói to điều này, hoặc nói trong đầu, hoặc viết/nhập nó ra. Hãy rõ ràng và cụ thể để không còn nghi ngờ hoặc có chỗ cho sự mơ hồ. Bạn thậm chí có thể giải thích cho chính mình _tại sao_ đó là những gì bạn mong đợi.

"Nó nên hoạt động" không phải là một mong đợi tốt.

"Tôi mong đợi một phản hồi chuyển hướng 301 khi tôi thực hiện yêu cầu đến URI này" thì tốt hơn nhiều.


<a id="current-behavior"></a>
### Hành vi hiện tại

Quan sát những gì đang xảy ra. Chuyện gì _chính xác_ đang xảy ra, và nó tương phản như thế nào với mong đợi của bạn? Tổng hợp những gì bạn biết.

"Nó không hoạt động" là cụm từ vô ích và lười biếng; hãy tránh cụm từ này ở mọi nơi trừ khi có lẽ nó được sử dụng như một mô tả viết tắt cho một hành vi cụ thể đã được ghi chép chi tiết.

"Thay vì phản hồi 301, tôi nhận được phản hồi 200, mặc dù tôi thấy tiêu đề `Server: Caddy`," tốt hơn nhiều vì nó so sánh và đối chiếu những gì bạn biết với những gì bạn mong đợi, và nó tổng hợp các thông tin đã biết khác, điều này cho chúng tôi biết rằng yêu cầu ít nhất đã đến được một phiên bản Caddy.


<a id="logs"></a>
### Nhật ký (Logs)

Có gì trong nhật ký của Caddy? Theo mặc định, chúng được ghi vào thiết bị đầu cuối (terminal) đã bắt đầu tiến trình. Nếu chạy "tách biệt" như một dịch vụ hệ thống, bạn có thể phải lấy nhật ký từ nơi khác.

Lưu ý rằng nhật ký yêu cầu HTTP ("access logs") khác với nhật ký tiến trình (process logs), và cần phải được bật rõ ràng trong cấu hình của bạn.

Bạn cũng có thể muốn bật nhật ký cấp độ DEBUG nếu bạn chưa làm như vậy.

Nhưng dù bằng cách nào, một trong những điều đầu tiên bạn nên làm là xem nhật ký. _Tất cả chúng._ Ngữ cảnh tin nhắn rất quan trọng, vì vậy một dòng nhật ký duy nhất đứng riêng lẻ hiếm khi hữu ích. Hãy thu thập nhiều hơn mức bạn nghĩ là cần thiết và lưu giữ nó trong suốt quá trình khắc phục sự cố.

Có gợi ý nào trong nhật ký không?


Recognize and doubt assumptions
-------------------------------

Trước khi đi xa hơn, chúng tôi phải nhấn mạnh tầm quan trọng của việc phê phán những gì bạn giả định. Tất cả chúng ta đều đưa ra các giả định dựa trên những gì chúng ta đã quen thuộc và những gì chúng ta mong đợi. "Hãy lưu tâm đến các giả định của bạn, và sức mạnh của bạn sẽ rất lớn." (&mdash;Yoda, hoặc ai đó.)

Ví dụ, một giả định phổ biến là sau khi biên dịch lại Caddy, việc chạy `caddy` sẽ làm cho mã mới được thực thi. Điều này chỉ đúng nếu tệp thực thi đã biên dịch của bạn thay thế tệp trong `$PATH` của bạn. Thay vào đó, `./caddy` thường là cách gọi lệnh đúng.

Các giả định sẽ chồng chất lên nhau khi việc triển khai hoặc cấu hình của bạn trở nên phức tạp hơn. Ví dụ, triển khai trong Docker liên quan đến việc xây dựng lại một image và chạy nó, điều này nhân lên các giả định mà bạn có thể đưa ra.

Nhiều câu hỏi và báo cáo lỗi cuối cùng lại là vấn đề với cấu hình hệ thống và mạng bên ngoài, chứ không phải bản thân Caddy. Ví dụ, nếu bạn không thể kết nối với phiên bản Caddy của mình, nhưng Caddy rõ ràng đang chạy, có lẽ bạn giả định rằng đó không phải là DNS. Gợi ý: hầu như luôn luôn là DNS.

Ngay cả việc chỉ giả định rằng bạn đã tải lại cấu hình, nhưng thực tế bạn chưa làm, cũng là một sai lầm phổ biến. Hãy cố gắng nghiêm túc về quy trình của bạn. Xác minh ở mọi cấp độ.


Tái hiện hành vi
----------------------

Đây là một bước quan trọng thường giúp các vấn đề tự được giải quyết: hãy làm cho vấn đề xảy ra một lần nữa.

Cụ thể, hãy làm cho nó xảy ra lần nữa *theo cách tối giản nhất có thể*. Loại bỏ cấu hình không cần thiết, các bước triển khai, các yếu tố môi trường, v.v., cho đến khi vấn đề biến mất.

Một chiến lược phổ biến là chỉ loại bỏ từng thứ một và thử lại, cho đến khi vấn đề biến mất. Khi đó, thứ bạn vừa loại bỏ có khả năng là nguyên nhân, hoặc&mdash;và đây là một nơi tốt để nghi ngờ các giả định&mdash;sự kết hợp giữa thứ cuối cùng và những gì bạn đã loại bỏ trước đó là nguyên nhân. Xác minh bằng cách thêm lại những thứ đầu tiên đã bị loại bỏ. Thu hẹp nó lại.

Một ý tưởng khác là loại bỏ khoảng một nửa mọi thứ sau mỗi lần lặp, và một khi vấn đề biến mất, hãy loại bỏ chỉ một nửa của một nửa đó, và cứ tiếp tục như vậy. Điều này giống như tìm kiếm nhị phân và có thể nhanh hơn.

Ngoài ra, thay vì loại bỏ, bạn có thể đảo ngược các chiến lược này và xây dựng dần cấu hình hoặc kịch bản của mình từ đầu, thử lại mỗi lần cho đến khi vấn đề xuất hiện.

Thường thì chỉ riêng quy trình này sẽ xác định được vấn đề và cách khắc phục có thể trở nên rõ ràng. Nếu không, ít nhất bạn có thể viết ra các bước tối giản để tái hiện vấn đề.


Khám phá hành vi
-----------------

Với các bước đã biết để tái hiện vấn đề, bạn đang ở vị trí tốt để chẩn đoán nguyên nhân. Điều này bao gồm việc mày mò và, nếu bạn hiểu biết, hãy đọc mã nguồn.

Nếu bạn không thể giải thích tại sao vấn đề đang xảy ra, hãy thay đổi hành vi. Thực hiện một thay đổi nhỏ và thử lại. Ví dụ, nếu cấu hình liên quan của bạn sử dụng một biểu thức chính quy (regular expression), hãy thay đổi/đơn giản hóa biểu thức đó&mdash;or loại bỏ hoàn toàn&mdash;và xem liệu bạn có làm được _điều gì đó_ để có được hành vi bạn đang tìm kiếm hay không. Ngay cả khi đó không phải là những gì bạn muốn, ít nhất bạn cũng biết đó là vấn đề với biểu thức chính quy hoặc cấu hình.

Khi bạn khám phá, hãy chú ý đến các quy luật về những gì hoạt động và những gì không. Điều này sẽ dẫn dắt bạn trên con đường tìm kiếm giải pháp.

Nếu bạn tìm thấy giải pháp, sau đó bạn có thể quyết định xem nó có nên là một lỗi (bug) hay không. Đôi khi không rõ ràng liệu đó có phải là lỗi hay không; việc đăng một vấn đề (issue) với các thử nghiệm của bạn và nhận phản hồi từ người bảo trì dù theo cách nào cũng là điều bình thường.

Và nếu nó không phải là lỗi, chúc mừng! Bạn đã giải quyết được một vấn đề và học được ít nhất một điều gì đó trong quá trình này.

Hãy cân nhắc đăng về trải nghiệm của bạn [trên diễn đàn](https://caddy.community) để giúp đỡ những người khác có thể gặp phải vấn đề tương tự.
