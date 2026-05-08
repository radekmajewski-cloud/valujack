CARDS_PATH = '/Users/radekmajewski/Downloads/valujack/public/index.html'

with open(CARDS_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

old = '''        // STEP 5: Keeper + rotation
        // keeperSeed changes every 2 days — best card stays 2 days
        // todaySeed changes every day — other 2 slots rotate daily
        const dayNumber  = Math.floor(todaySeed / 86400);
        const keeperSeed = Math.floor(dayNumber / 2) * 86400;

        function pickKeeper(pool, kseed) {
            return pickPool(pool, kseed, 1)[0] || null;
        }

        function pickRotators(pool, seed, keeper, count) {
            const withoutKeeper = pool.filter(c => !keeper || c.ticker !== keeper.ticker);
            // Build 7-day exclusion set — cards that showed as rotators in past 7 days
            const dayNum = Math.floor(seed / 86400);
            const recentTickers = new Set();
            for (let d = 1; d <= 7; d++) {
                const pastSeed = (dayNum - d) * 86400;
                const pastKeeperSeed = Math.floor((dayNum - d) / 2) * 86400;
                const pastKeeper = pickPool(pool, pastKeeperSeed, 1)[0];
                const pastEligible = pool.filter(c => !pastKeeper || c.ticker !== pastKeeper.ticker);
                const pastRotators = pickPool(pastEligible, pastSeed, count);
                pastRotators.forEach(c => recentTickers.add(c.ticker));
            }
            // Exclude recent rotators, but keep pool if exclusion leaves too few
            const freshPool = withoutKeeper.filter(c => !recentTickers.has(c.ticker));
            const usePool = freshPool.length >= count ? freshPool : withoutKeeper;
            return pickPool(usePool, seed, count);
        }

        // One guaranteed card per strategy, each with its own keeper/rotator cycle
        const kingPool  = dedupedCards.filter(c => c.type === 'KING');
        const jackPool  = dedupedCards.filter(c => c.type === 'JACK');
        const twoPool   = dedupedCards.filter(c => c.type === 'TWO');
        const queenPool = dedupedCards.filter(c => c.type === 'QUEEN');
        const acePool   = dedupedCards.filter(c => c.type === 'ACE');
        const jokerPool = dedupedCards.filter(c => c.type === 'JOKER');

        // Pick one per strategy, avoiding sector duplicates across the hand
        function pickOne(pool, kseed, dseed, usedSectors) {
            // First try keeper
            const keeper = pickKeeper(pool, kseed);
            if (keeper && !usedSectors.has(keeper.sector)) return keeper;
            // Then try rotators avoiding used sectors
            const filtered = pool.filter(c => !usedSectors.has(c.sector));
            if (filtered.length === 0) return pickKeeper(pool, kseed) || pickRotators(pool, dseed, null, 1)[0] || null;
            return pickRotators(filtered, dseed, null, 1)[0] || null;
        }

        const usedSectors = new Set();
        // 2-card system with 7-day exclusion
        const dayOfYear = todaySeed % 1000;
        const dayInCycle = dayOfYear % 3;
        
        // Calculate last 7 days history
        const excludeTickers = new Set();
        for (let i = 1; i <= 7; i++) {
            const pastDay = dayOfYear - i;
            const pastCycle = pastDay % 3;
            const pastSeed = todaySeed - i;
            let pastPool;
            if (pastCycle === 0) pastPool = kingPool.concat(jokerPool);
            else if (pastCycle === 1) pastPool = jackPool.concat(queenPool);
            else pastPool = twoPool.concat(acePool);
            const pastPicks = pickPool(pastPool, pastSeed, 2);
            pastPicks.forEach(c => excludeTickers.add(c.ticker));
        }
        
        let todayFreeCard, todayProCard;
        
        if (dayInCycle === 0) {
            const availKing = kingPool.filter(c => !excludeTickers.has(c.ticker) && !usedSectors.has(c.sector));
            todayFreeCard = pickPool(availKing.length ? availKing : kingPool, todaySeed, 1)[0];
            if (todayFreeCard) usedSectors.add(todayFreeCard.sector);
            const availJoker = jokerPool.filter(c => !excludeTickers.has(c.ticker) && !usedSectors.has(c.sector));
            todayProCard = pickPool(availJoker.length ? availJoker : jokerPool, todaySeed*3, 1)[0];
        } else if (dayInCycle === 1) {
            const availJack = jackPool.filter(c => !excludeTickers.has(c.ticker) && !usedSectors.has(c.sector));
            todayFreeCard = pickPool(availJack.length ? availJack : jackPool, todaySeed, 1)[0];
            if (todayFreeCard) usedSectors.add(todayFreeCard.sector);
            const availQueen = queenPool.filter(c => !excludeTickers.has(c.ticker) && !usedSectors.has(c.sector));
            todayProCard = pickPool(availQueen.length ? availQueen : queenPool, todaySeed*3, 1)[0];
        } else {
            const availTwo = twoPool.filter(c => !excludeTickers.has(c.ticker) && !usedSectors.has(c.sector));
            todayFreeCard = pickPool(availTwo.length ? availTwo : twoPool, todaySeed, 1)[0];
            if (todayFreeCard) usedSectors.add(todayFreeCard.sector);
            const availAce = acePool.filter(c => !excludeTickers.has(c.ticker) && !usedSectors.has(c.sector));
            todayProCard = pickPool(availAce.length ? availAce : acePool, todaySeed*3, 1)[0];
        }'''

new = '''        // STEP 5: 14-day no-repeat rotation
        // No keeper system — every card rotates daily
        // No fixed strategy cycle — free pick from all strategies each day
        // 14-day exclusion — no card repeats within 14 days

        const kingPool  = dedupedCards.filter(c => c.type === 'KING');
        const jackPool  = dedupedCards.filter(c => c.type === 'JACK');
        const twoPool   = dedupedCards.filter(c => c.type === 'TWO');
        const queenPool = dedupedCards.filter(c => c.type === 'QUEEN');
        const acePool   = dedupedCards.filter(c => c.type === 'ACE');
        const jokerPool = dedupedCards.filter(c => c.type === 'JOKER');

        const freeStrategies  = [kingPool, jackPool, twoPool];
        const proStrategies   = [queenPool, acePool, jokerPool];
        const freeNames = ['KING', 'JACK', 'TWO'];
        const proNames  = ['QUEEN', 'ACE', 'JOKER'];

        // Build 14-day exclusion set from deterministic past picks
        const excludeTickers = new Set();
        for (let i = 1; i <= 14; i++) {
            const pastSeed = todaySeed - i;
            // Recreate past free pick
            const pastFreeIdx = Math.abs(pastSeed * 1664525) % 3;
            const pastFreePool = freeStrategies[pastFreeIdx];
            const pastFree = pickPool(pastFreePool, pastSeed, 1)[0];
            if (pastFree) excludeTickers.add(pastFree.ticker);
            // Recreate past pro pick
            const pastProIdx = Math.abs(pastSeed * 22695477) % 3;
            const pastProPool = proStrategies[pastProIdx];
            const pastPro = pickPool(pastProPool, pastSeed * 3, 1)[0];
            if (pastPro) excludeTickers.add(pastPro.ticker);
        }

        const usedSectors = new Set();

        // Pick free card — rotate through strategies, exclude recent cards
        const freeIdx = Math.abs(todaySeed * 1664525) % 3;
        const todayFreeStrategy = freeStrategies[freeIdx];
        const availFree = todayFreeStrategy.filter(c => !excludeTickers.has(c.ticker) && !usedSectors.has(c.sector));
        const todayFreeCard = pickPool(availFree.length ? availFree : todayFreeStrategy, todaySeed, 1)[0];
        if (todayFreeCard) usedSectors.add(todayFreeCard.sector);

        // Pick pro card — rotate through strategies, exclude recent cards and used sectors
        const proIdx = Math.abs(todaySeed * 22695477) % 3;
        const todayProStrategy = proStrategies[proIdx];
        const availPro = todayProStrategy.filter(c => !excludeTickers.has(c.ticker) && !usedSectors.has(c.sector));
        const todayProCard = pickPool(availPro.length ? availPro : todayProStrategy, todaySeed * 3, 1)[0];'''

if old in content:
    content = content.replace(old, new)
    with open(CARDS_PATH, 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Rotation logic updated successfully")
else:
    print("❌ Pattern not found — no changes made")
