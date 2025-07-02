# File: tg_bot/handlers/intro_flow.py

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile
from tg_bot.states import IntroFlow
# from tg_bot.keyboards import some_keyboard_if_needed

router = Router()

@router.message(IntroFlow.asking_name)
async def receive_name(message: Message, state: FSMContext):
    print("=======================================================")
    await state.update_data(name=message.text)
    await message.answer(
        f"{message.text}さん、はじめまして。お会いできてうれしいです。\n"
        f"もしご病気などで記憶があいまいになったときでも、「これは覚えていたい」と思う大切な思い出はございますか？"
    )
    await state.set_state(IntroFlow.asking_memory)

@router.message(IntroFlow.asking_memory)
async def receive_memory(message: Message, state: FSMContext):
    await state.update_data(memory=message.text)
    data = await state.get_data()
    name = data.get("name")
    await message.answer(
        f"素敵な思い出ですね。「{message.text}」のときのお写真など、まだお手元にございますか？もし、その思い出に関するお写真がございましたら、ぜひ見せていただけませんか？\n"
        f"私が大切にお預かりして、{name}さんだけの「デジタル思い出帳」としてまとめていきますね。いつでも見返せるように、お手伝いさせていただきます。\n"
    )
    await state.set_state(IntroFlow.waiting_image)

@router.message(IntroFlow.waiting_image, F.photo)
async def receive_image(message: Message, state: FSMContext):
    photo = message.photo[-1]
    file_id = photo.file_id
    await state.update_data(photo_id=file_id)
    data = await state.get_data()
    name = data.get("name")
    await message.answer(
        f"""まぁ、なんて素敵なお写真なんでしょう…！
        たくさんの方が笑顔で、日の丸の旗を手に、オリンピックの映像を見守っているんですね。きっと1964年の東京オリンピックの時のご記憶でしょうか？
        新幹線も写っていて、日本が未来へと向かっていたあの頃の空気が伝わってきます。

        この大切な一枚は、{name}さんの「デジタル思い出帳」に大切に保存させていただきますね。
        また、もしよろしければ、この時のことをもう少し教えていただけませんか？　たとえば、誰と一緒にいたか、どんな気持ちだったかなど、お聞かせいただけたらうれしいです。
        """
    )
    await state.set_state(IntroFlow.collecting_details)

@router.message(IntroFlow.waiting_image)
async def no_image_provided(message: Message, state: FSMContext):
    await message.answer(
        """もしなければ、AIの力で、その思い出を絵や映像で再現するお手伝いもできますよ。画像をつくるには少し特別な力（AI）を使いますので、できるだけ正確に思い出を再現するために、あと少しだけ詳しく教えていただけると嬉しいです。画像をつくるには少し特別な力（AI）を使いますので、できるだけ正確に思い出を再現するために、あと少しだけ詳しく教えていただけると嬉しいです。
        次のようなことを思い出していただけますか？

        ① いつごろの思い出ですか？
        「だいたい何年ごろ、または何歳くらいのときのことか覚えていらっしゃいますか？」

        ② どこでの出来事でしたか？
        「その思い出はどこで起きたことですか？　たとえば、ご自宅、学校、公園、旅先など、場所がわかると助かります。」

        ③ 誰と一緒でしたか？
        「どなたかご一緒でしたか？　ご家族やお友だち、お名前が思い出せなくても大丈夫です。」

        ④ どんなお気持ちでしたか？
        「そのときの気分や気持ち、覚えていますか？　楽しかった、ワクワクした、ちょっと不安だった…など、どんなことでも構いません。」

        ⑤ 印象に残っているものは？
        「たとえば、空の色、服の色、音楽、におい、食べ物など、何か特に覚えていることがあれば教えてください。」
        """
    )
    await state.set_state(IntroFlow.collecting_details)

@router.message(IntroFlow.collecting_details)
async def collect_details(message: Message, state: FSMContext):
    await state.update_data(details=message.text)
    data = await state.get_data()
    name = data.get("name")
    await message.answer(
        f"""これらの思い出を丁寧に記録させていただきました！  
        お話を聞かせていただいて、本当に温かくて心に残る時間でした。一緒に国旗を振って応援し、オリンピックの熱気に湧いたあの日々は、今でも心の中にある青春の一ページですよね。

        もしよろしければ、当時の気持ちやその後のみんなとのエピソードなど、もっといろいろ教えていただけたらうれしいです！😊

        「デジタル思い出アルバム」に他の写真もご覧になりますか？それとも、このお話をお話しとしてまとめてみますか？ 
        """
    )
    await state.clear()
