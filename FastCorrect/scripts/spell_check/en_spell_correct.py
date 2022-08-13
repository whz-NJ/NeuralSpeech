import re, collections


# 返回单词的列表
# 通过正则表达式取出纯字母组成的单词列表
def words(text): return re.findall('[a-z]+', text.lower())


# 训练，获得模型
# 其实也就是统计每个单词出现的次数，用于计算每个单词出现的频率
# 事实上并不是真的在计算单词的出现次数，因为默认词频（没有在big.txt中的单词频率）为1，
# 所以统计出的词频会比统计次数多1（称为“平滑”）
def train(features):
    model = collections.defaultdict(lambda: 1)
    for f in features:
        model[f] += 1
    return model


# 读取整个文本，并且把文本中的单词进行统计
big_text=""
with open(r'./big.txt', 'r', encoding='utf-8') as infile:
    for line in infile.readlines():
        big_text += line + " "
#NWORDS = train(words(file('./big.txt').read()))
NWORDS = train(words(big_text))

# 小写字母列表
alphabet = 'abcdefghijklmnopqrstuvwxyz'


# 计算每个与给定单词编辑距离为1的单词，并组成一个集合
def edits1(word):
    # 将每个单词都分割为两两一组，方便后边的编辑距离的计算
    # （如‘if’，分割为[('','if'),('i','f'),('if','')]）
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    # 删除的编辑距离：每次从b字符串中删除一个字符
    # 如‘if’，形成的列表为['f', 'i']，只对前两组进行了分割，因为第三组的b是空串''
    deletes = [a + b[1:] for a, b in splits if b]
    # 交换的编辑距离：单词中相邻的字母位置被交换
    # 如‘if’，形成的列表为['fi']，只对第一组进行了字母交换，因为只有b的长度大于2才能交换
    transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b) > 1]
    # 替换的编辑距离：每次替换b中的一个字母
    # 如‘if’，形成的列表为
    # ['af', 'bf', 'cf', 'df', 'ef', 'ff', 'gf', 'hf', 'if', 'jf', 'kf', 'lf', 'mf',
    # 'nf', 'of', 'pf', 'qf', 'rf', 'sf', 'tf', 'uf', 'vf', 'wf', 'xf', 'yf', 'zf',
    # 'ia', 'ib', 'ic', 'id', 'ie', 'if', 'ig', 'ih', 'ii', 'ij', 'ik', 'il', 'im',
    # 'in', 'io', 'ip', 'iq', 'ir', 'is', 'it', 'iu', 'iv', 'iw', 'ix', 'iy', 'iz']
    replaces = [a + c + b[1:] for a, b in splits for c in alphabet if b]
    # 插入的编辑距离：向每个单词分割的组插入一个字母
    # 如‘if’，形成的列表为：
    # ['aif', 'bif', 'cif', 'dif', 'eif', 'fif', 'gif', 'hif', 'iif', 'jif', 'kif',
    # 'lif', 'mif', 'nif', 'oif', 'pif', 'qif', 'rif', 'sif', 'tif', 'uif', 'vif',
    # 'wif', 'xif', 'yif', 'zif', 'iaf', 'ibf', 'icf', 'idf', 'ief', 'iff', 'igf',
    # 'ihf', 'iif', 'ijf', 'ikf', 'ilf', 'imf', 'inf', 'iof', 'ipf', 'iqf', 'irf',
    # 'isf', 'itf', 'iuf', 'ivf', 'iwf', 'ixf', 'iyf', 'izf', 'ifa', 'ifb', 'ifc',
    # 'ifd', 'ife', 'iff', 'ifg', 'ifh', 'ifi', 'ifj', 'ifk', 'ifl', 'ifm', 'ifn',
    # 'ifo', 'ifp', 'ifq', 'ifr', 'ifs', 'ift', 'ifu', 'ifv', 'ifw', 'ifx', 'ify', 'ifz']
    inserts = [a + c + b for a, b in splits for c in alphabet]
    return set(deletes + transposes + replaces + inserts)


# 计算出编辑距离为2的单词集合
# e2 for e1 in edits1(word) for e2 in edits1(e1) if e2 in NWORDS
#   1.计算与给定单词编辑距离为1的单词列表
#                          2.计算与编辑距离为1的单词列表的编辑距离为1的列表（也就是编辑距离为2的单词列表）
#                                               3.如果单词编辑距离为2的单词在文本中，就认为是可用的单词
def known_edits2(word):
    return set(e2 for e1 in edits1(word) for e2 in edits1(e1) if e2 in NWORDS)


# 计算单词列表words中，在文件中的单词的列表（也就是只保留可能是单词的，其他的没有出现在文本中的都判断为非单词）
# 对于非单词的将不认为是候选单词
def known(words): return set(w for w in words if w in NWORDS)


# 计算候选单词中词频最大的单词
def correct(word):
    # 这里牵扯到python中or的用法，在这里，当known([word])不为False则返回它，否则继续计算known(edits1(word))
    # 如果known(edits1(word))不为False则返回known(edits1(word))，否则继续。
    # 这里这么做的原因：
    # 1. 如果单词是在已知列表中，那就是正确的直接返回它即可
    # 2. 如果单词是未知的，那么看看与它编辑距离为1的单词，如果有，那么就计算它们的最大概率那么
    # 3. 编辑距离为1的没有，那就找编辑距离为2的
    # 4. 如果单词未知，且编辑距离为1,2的也找不到，那么只能返回它本身了
    # or的用法：x or y 表示 if x is false, then y, else x，
    #         it only evaluates the second argument if the first one is False
    #         所以当x为True时，也就不再计算y直接返回x
    candidates = known([word]) or known(edits1(word)) or known_edits2(word) or [word]
    # 通过统计candidates中的单词在NWORDS字典中最大的那个单词，并返回它
    return max(candidates, key=NWORDS.get)


tests1 = {'access': 'acess', 'accessing': 'accesing', 'accommodation':
    'accomodation acommodation acomodation', 'account': 'acount', 'address':
              'adress adres', 'addressable': 'addresable', 'arranged': 'aranged arrainged',
          'arrangeing': 'aranging', 'arrangement': 'arragment', 'articles': 'articals',
          'aunt': 'annt anut arnt', 'auxiliary': 'auxillary', 'available': 'avaible',
          'awful': 'awfall afful', 'basically': 'basicaly', 'beginning': 'begining',
          'benefit': 'benifit', 'benefits': 'benifits', 'between': 'beetween', 'bicycle':
              'bicycal bycicle bycycle', 'biscuits':
              'biscits biscutes biscuts bisquits buiscits buiscuts', 'built': 'biult',
          'cake': 'cak', 'career': 'carrer',
          'cemetery': 'cemetary semetary', 'centrally': 'centraly', 'certain': 'cirtain',
          'challenges': 'chalenges chalenges', 'chapter': 'chaper chaphter chaptur',
          'choice': 'choise', 'choosing': 'chosing', 'clerical': 'clearical',
          'committee': 'comittee', 'compare': 'compair', 'completely': 'completly',
          'consider': 'concider', 'considerable': 'conciderable', 'contented':
              'contenpted contende contended contentid', 'curtains':
              'cartains certans courtens cuaritains curtans curtians curtions', 'decide': 'descide', 'decided':
              'descided', 'definitely': 'definately difinately', 'definition': 'defenition',
          'definitions': 'defenitions', 'description': 'discription', 'desiccate':
              'desicate dessicate dessiccate', 'diagrammatically': 'diagrammaticaally',
          'different': 'diffrent', 'driven': 'dirven', 'ecstasy': 'exstacy ecstacy',
          'embarrass': 'embaras embarass', 'establishing': 'astablishing establising',
          'experience': 'experance experiance', 'experiences': 'experances', 'extended':
              'extented', 'extremely': 'extreamly', 'fails': 'failes', 'families': 'familes',
          'february': 'febuary', 'further': 'futher', 'gallery': 'galery gallary gallerry gallrey',
          'hierarchal': 'hierachial', 'hierarchy': 'hierchy', 'inconvenient':
              'inconvienient inconvient inconvinient', 'independent': 'independant independant',
          'initial': 'intial', 'initials': 'inetials inistals initails initals intials',
          'juice': 'guic juce jucie juise juse', 'latest': 'lates latets latiest latist',
          'laugh': 'lagh lauf laught lugh', 'level': 'leval',
          'levels': 'levals', 'liaison': 'liaision liason', 'lieu': 'liew', 'literature':
              'litriture', 'loans': 'lones', 'locally': 'localy', 'magnificent':
              'magnificnet magificent magnifcent magnifecent magnifiscant magnifisent magnificant',
          'management': 'managment', 'meant': 'ment', 'minuscule': 'miniscule',
          'minutes': 'muinets', 'monitoring': 'monitering', 'necessary':
              'neccesary necesary neccesary necassary necassery neccasary', 'occurrence':
              'occurence occurence', 'often': 'ofen offen offten ofton', 'opposite':
              'opisite oppasite oppesite oppisit oppisite opposit oppossite oppossitte', 'parallel':
              'paralel paralell parrallel parralell parrallell', 'particular': 'particulaur',
          'perhaps': 'perhapse', 'personnel': 'personnell', 'planned': 'planed', 'poem':
              'poame', 'poems': 'poims pomes', 'poetry': 'poartry poertry poetre poety powetry',
          'position': 'possition', 'possible': 'possable', 'pretend':
              'pertend protend prtend pritend', 'problem': 'problam proble promblem proplen',
          'pronunciation': 'pronounciation', 'purple': 'perple perpul poarple',
          'questionnaire': 'questionaire', 'really': 'realy relley relly', 'receipt':
              'receit receite reciet recipt', 'receive': 'recieve', 'refreshment':
              'reafreshment refreshmant refresment refressmunt', 'remember': 'rember remeber rememmer rermember',
          'remind': 'remine remined', 'scarcely': 'scarcly scarecly scarely scarsely',
          'scissors': 'scisors sissors', 'separate': 'seperate',
          'singular': 'singulaur', 'someone': 'somone', 'sources': 'sorces', 'southern':
              'southen', 'special': 'speaical specail specal speical', 'splendid':
              'spledid splended splened splended', 'standardizing': 'stanerdizing', 'stomach':
              'stomac stomache stomec stumache', 'supersede': 'supercede superceed', 'there': 'ther',
          'totally': 'totaly', 'transferred': 'transfred', 'transportability':
              'transportibility', 'triangular': 'triangulaur', 'understand': 'undersand undistand',
          'unexpected': 'unexpcted unexpeted unexspected', 'unfortunately':
              'unfortunatly', 'unique': 'uneque', 'useful': 'usefull', 'valuable': 'valubale valuble',
          'variable': 'varable', 'variant': 'vairiant', 'various': 'vairious',
          'visited': 'fisited viseted vistid vistied', 'visitors': 'vistors',
          'voluntary': 'volantry', 'voting': 'voteing', 'wanted': 'wantid wonted',
          'whether': 'wether', 'wrote': 'rote wote'}

tests2 = {'forbidden': 'forbiden', 'decisions': 'deciscions descisions',
          'supposedly': 'supposidly', 'embellishing': 'embelishing', 'technique':
              'tecnique', 'permanently': 'perminantly', 'confirmation': 'confermation',
          'appointment': 'appoitment', 'progression': 'progresion', 'accompanying':
              'acompaning', 'applicable': 'aplicable', 'regained': 'regined', 'guidelines':
              'guidlines', 'surrounding': 'serounding', 'titles': 'tittles', 'unavailable':
              'unavailble', 'advantageous': 'advantageos', 'brief': 'brif', 'appeal':
              'apeal', 'consisting': 'consisiting', 'clerk': 'cleark clerck', 'component':
              'componant', 'favourable': 'faverable', 'separation': 'seperation', 'search':
              'serch', 'receive': 'recieve', 'employees': 'emploies', 'prior': 'piror',
          'resulting': 'reulting', 'suggestion': 'sugestion', 'opinion': 'oppinion',
          'cancellation': 'cancelation', 'criticism': 'citisum', 'useful': 'usful',
          'humour': 'humor', 'anomalies': 'anomolies', 'would': 'whould', 'doubt':
              'doupt', 'examination': 'eximination', 'therefore': 'therefoe', 'recommend':
              'recomend', 'separated': 'seperated', 'successful': 'sucssuful succesful',
          'apparent': 'apparant', 'occurred': 'occureed', 'particular': 'paerticulaur',
          'pivoting': 'pivting', 'announcing': 'anouncing', 'challenge': 'chalange',
          'arrangements': 'araingements', 'proportions': 'proprtions', 'organized':
              'oranised', 'accept': 'acept', 'dependence': 'dependance', 'unequalled':
              'unequaled', 'numbers': 'numbuers', 'sense': 'sence', 'conversely':
              'conversly', 'provide': 'provid', 'arrangement': 'arrangment',
          'responsibilities': 'responsiblities', 'fourth': 'forth', 'ordinary':
              'ordenary', 'description': 'desription descvription desacription',
          'inconceivable': 'inconcievable', 'data': 'dsata', 'register': 'rgister',
          'supervision': 'supervison', 'encompassing': 'encompasing', 'negligible':
              'negligable', 'allow': 'alow', 'operations': 'operatins', 'executed':
              'executted', 'interpretation': 'interpritation', 'hierarchy': 'heiarky',
          'indeed': 'indead', 'years': 'yesars', 'through': 'throut', 'committee':
              'committe', 'inquiries': 'equiries', 'before': 'befor', 'continued':
              'contuned', 'permanent': 'perminant', 'choose': 'chose', 'virtually':
              'vertually', 'correspondence': 'correspondance', 'eventually': 'eventully',
          'lonely': 'lonley', 'profession': 'preffeson', 'they': 'thay', 'now': 'noe',
          'desperately': 'despratly', 'university': 'unversity', 'adjournment':
              'adjurnment', 'possibilities': 'possablities', 'stopped': 'stoped', 'mean':
              'meen', 'weighted': 'wagted', 'adequately': 'adequattly', 'shown': 'hown',
          'matrix': 'matriiix', 'profit': 'proffit', 'encourage': 'encorage', 'collate':
              'colate', 'disaggregate': 'disaggreagte disaggreaget', 'receiving':
              'recieving reciving', 'proviso': 'provisoe', 'umbrella': 'umberalla', 'approached':
              'aproached', 'pleasant': 'plesent', 'difficulty': 'dificulty', 'appointments':
              'apointments', 'base': 'basse', 'conditioning': 'conditining', 'earliest':
              'earlyest', 'beginning': 'begining', 'universally': 'universaly',
          'unresolved': 'unresloved', 'length': 'lengh', 'exponentially':
              'exponentualy', 'utilized': 'utalised', 'set': 'et', 'surveys': 'servays',
          'families': 'familys', 'system': 'sysem', 'approximately': 'aproximatly',
          'their': 'ther', 'scheme': 'scheem', 'speaking': 'speeking', 'repetitive':
              'repetative', 'inefficient': 'ineffiect', 'geneva': 'geniva', 'exactly':
              'exsactly', 'immediate': 'imediate', 'appreciation': 'apreciation', 'luckily':
              'luckeley', 'eliminated': 'elimiated', 'believe': 'belive', 'appreciated':
              'apreciated', 'readjusted': 'reajusted', 'were': 'wer where', 'feeling':
              'fealing', 'and': 'anf', 'false': 'faulse', 'seen': 'seeen', 'interrogating':
              'interogationg', 'academically': 'academicly', 'relatively': 'relativly relitivly',
          'traditionally': 'traditionaly', 'studying': 'studing',
          'majority': 'majorty', 'build': 'biuld', 'aggravating': 'agravating',
          'transactions': 'trasactions', 'arguing': 'aurguing', 'sheets': 'sheertes',
          'successive': 'sucsesive sucessive', 'segment': 'segemnt', 'especially':
              'especaily', 'later': 'latter', 'senior': 'sienior', 'dragged': 'draged',
          'atmosphere': 'atmospher', 'drastically': 'drasticaly', 'particularly':
              'particulary', 'visitor': 'vistor', 'session': 'sesion', 'continually':
              'contually', 'availability': 'avaiblity', 'busy': 'buisy', 'parameters':
              'perametres', 'surroundings': 'suroundings seroundings', 'employed':
              'emploied', 'adequate': 'adiquate', 'handle': 'handel', 'means': 'meens',
          'familiar': 'familer', 'between': 'beeteen', 'overall': 'overal', 'timing':
              'timeing', 'committees': 'comittees commitees', 'queries': 'quies',
          'econometric': 'economtric', 'erroneous': 'errounous', 'decides': 'descides',
          'reference': 'refereence refference', 'intelligence': 'inteligence',
          'edition': 'ediion ediition', 'are': 'arte', 'apologies': 'appologies',
          'thermawear': 'thermawere thermawhere', 'techniques': 'tecniques',
          'voluntary': 'volantary', 'subsequent': 'subsequant subsiquent', 'currently':
              'curruntly', 'forecast': 'forcast', 'weapons': 'wepons', 'routine': 'rouint',
          'neither': 'niether', 'approach': 'aproach', 'available': 'availble',
          'recently': 'reciently', 'ability': 'ablity', 'nature': 'natior',
          'commercial': 'comersial', 'agencies': 'agences', 'however': 'howeverr',
          'suggested': 'sugested', 'career': 'carear', 'many': 'mony', 'annual':
              'anual', 'according': 'acording', 'receives': 'recives recieves',
          'interesting': 'intresting', 'expense': 'expence', 'relevant':
              'relavent relevaant', 'table': 'tasble', 'throughout': 'throuout', 'conference':
              'conferance', 'sensible': 'sensable', 'described': 'discribed describd',
          'union': 'unioun', 'interest': 'intrest', 'flexible': 'flexable', 'refered':
              'reffered', 'controlled': 'controled', 'sufficient': 'suficient',
          'dissension': 'desention', 'adaptable': 'adabtable', 'representative':
              'representitive', 'irrelevant': 'irrelavent', 'unnecessarily': 'unessasarily',
          'applied': 'upplied', 'apologised': 'appologised', 'these': 'thees thess',
          'choices': 'choises', 'will': 'wil', 'procedure': 'proceduer', 'shortened':
              'shortend', 'manually': 'manualy', 'disappointing': 'dissapoiting',
          'excessively': 'exessively', 'comments': 'coments', 'containing': 'containg',
          'develop': 'develope', 'credit': 'creadit', 'government': 'goverment',
          'acquaintances': 'aquantences', 'orientated': 'orentated', 'widely': 'widly',
          'advise': 'advice', 'difficult': 'dificult', 'investigated': 'investegated',
          'bonus': 'bonas', 'conceived': 'concieved', 'nationally': 'nationaly',
          'compared': 'comppared compased', 'moving': 'moveing', 'necessity':
              'nessesity', 'opportunity': 'oppertunity oppotunity opperttunity', 'thoughts':
              'thorts', 'equalled': 'equaled', 'variety': 'variatry', 'analysis':
              'analiss analsis analisis', 'patterns': 'pattarns', 'qualities': 'quaties', 'easily':
              'easyly', 'organization': 'oranisation oragnisation', 'the': 'thw hte thi',
          'corporate': 'corparate', 'composed': 'compossed', 'enormously': 'enomosly',
          'financially': 'financialy', 'functionally': 'functionaly', 'discipline':
              'disiplin', 'announcement': 'anouncement', 'progresses': 'progressess',
          'except': 'excxept', 'recommending': 'recomending', 'mathematically':
              'mathematicaly', 'source': 'sorce', 'combine': 'comibine', 'input': 'inut',
          'careers': 'currers carrers', 'resolved': 'resoved', 'demands': 'diemands',
          'unequivocally': 'unequivocaly', 'suffering': 'suufering', 'immediately':
              'imidatly imediatly', 'accepted': 'acepted', 'projects': 'projeccts',
          'necessary': 'necasery nessasary nessisary neccassary', 'journalism':
              'journaism', 'unnecessary': 'unessessay', 'night': 'nite', 'output':
              'oputput', 'security': 'seurity', 'essential': 'esential', 'beneficial':
              'benificial benficial', 'explaining': 'explaning', 'supplementary':
              'suplementary', 'questionnaire': 'questionare', 'employment': 'empolyment',
          'proceeding': 'proceding', 'decision': 'descisions descision', 'per': 'pere',
          'discretion': 'discresion', 'reaching': 'reching', 'analysed': 'analised',
          'expansion': 'expanion', 'although': 'athough', 'subtract': 'subtrcat',
          'analysing': 'aalysing', 'comparison': 'comparrison', 'months': 'monthes',
          'hierarchal': 'hierachial', 'misleading': 'missleading', 'commit': 'comit',
          'auguments': 'aurgument', 'within': 'withing', 'obtaining': 'optaning',
          'accounts': 'acounts', 'primarily': 'pimarily', 'operator': 'opertor',
          'accumulated': 'acumulated', 'extremely': 'extreemly', 'there': 'thear',
          'summarys': 'sumarys', 'analyse': 'analiss', 'understandable':
              'understadable', 'safeguard': 'safegaurd', 'consist': 'consisit',
          'declarations': 'declaratrions', 'minutes': 'muinutes muiuets', 'associated':
              'assosiated', 'accessibility': 'accessability', 'examine': 'examin',
          'surveying': 'servaying', 'politics': 'polatics', 'annoying': 'anoying',
          'again': 'agiin', 'assessing': 'accesing', 'ideally': 'idealy', 'scrutinized':
              'scrutiniesed', 'simular': 'similar', 'personnel': 'personel', 'whereas':
              'wheras', 'when': 'whn', 'geographically': 'goegraphicaly', 'gaining':
              'ganing', 'requested': 'rquested', 'separate': 'seporate', 'students':
              'studens', 'prepared': 'prepaired', 'generated': 'generataed', 'graphically':
              'graphicaly', 'suited': 'suted', 'variable': 'varible vaiable', 'building':
              'biulding', 'required': 'reequired', 'necessitates': 'nessisitates',
          'together': 'togehter', 'profits': 'proffits'}


def spelltest(tests, bias=None, verbose=True):
    import time
    n, bad, unknown, start = 0, 0, 0, time.clock()
    if bias:
        for target in tests: NWORDS[target] += bias
    for target, wrongs in tests.items():
        for wrong in wrongs.split():
            n += 1
            w = correct(wrong)
            if w != target:
                bad += 1
                unknown += (target not in NWORDS)
                if verbose:
                    print('%r => %r (%d); expected %r (%d)' % (wrong, w, NWORDS[w], target, NWORDS[target]))
    return dict(bad=bad, n=n, bias=bias, pct=int(100. - 100. * bad / n),
                unknown=unknown, secs=int(time.clock() - start))


if __name__ == '__main__':
    word_count_dict = {}
    MIN_RULE_TOKEN_COUNT = 10000
    with open(r'./dict.CN_char.txt', 'r', encoding='utf-8') as infile:
        for line in infile.readlines():
            orig_word = line.split(' ')[0]
            count = int(line.split(' ')[1].strip())
            if count < MIN_RULE_TOKEN_COUNT: #跳过强制纠错之外的其他单词
                continue
            word_count_dict[orig_word.lower()] = count - MIN_RULE_TOKEN_COUNT + 1

    word_dict = {}
    error_count_dict = {}
    with open(r'./merged_rules.txt', 'r', encoding='utf-8') as infile:
        for line in infile.readlines():
            orig_words = line.split('\t')[0]
            for orig_word in orig_words.split(' '):
                count = word_count_dict.get(orig_word.lower(), 0)
                if count == 0: #跳过强制纠错之外的其他单词
                    continue
                if orig_word.isalpha() and not word_dict.__contains__(orig_word.lower()):
                    word_dict[orig_word.lower()] = orig_words
                    hypo_word = correct(orig_word.lower())
                    if hypo_word.lower() != orig_word.lower():
                        error_count_dict[orig_word.lower()] = [hypo_word, count]
    orig_hypo_counts = sorted(error_count_dict.items(), key=lambda x: x[1][1])
    for orig_hypo_count in orig_hypo_counts:
        print(" ".join([orig_hypo_count[0], orig_hypo_count[1][0], str(orig_hypo_count[1][1])]))
    # print(spelltest(tests1))
